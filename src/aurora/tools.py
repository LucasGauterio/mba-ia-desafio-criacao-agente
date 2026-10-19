"""Tools determinísticas com as 5 garantias de negócio em código."""

import random
import sqlite3
from typing import Any, Dict, List

from google.adk.tools import ToolContext

from aurora.database import get_db_connection
from aurora.regulamento import obter_capitulo


def _gerar_codigo_reserva_unico(conn: sqlite3.Connection) -> str:
    """Gera um código único que jamais foi utilizado no histórico (RN05)."""
    while True:
        num = random.randint(1000, 9999)
        codigo = f"RSV-{num}"
        cur = conn.execute("SELECT 1 FROM codigos_reserva_usados WHERE codigo = ?", (codigo,))
        if not cur.fetchone():
            return codigo


def listar_areas_comuns() -> List[Dict[str, Any]]:
    """Lista as áreas comuns disponíveis para reserva e suas respectivas taxas."""
    with get_db_connection() as conn:
        cur = conn.execute("SELECT id, nome, taxa FROM areas ORDER BY nome ASC")
        return [dict(row) for row in cur.fetchall()]


def consultar_minhas_reservas(tool_context: ToolContext) -> List[Dict[str, Any]]:
    """Lista as reservas ativas do apartamento da sessão atual."""
    apartamento = tool_context.state.get("apartamento", "")
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT codigo, area, data FROM reservas WHERE apartamento = ? ORDER BY data ASC",
            (apartamento,),
        )
        return [dict(row) for row in cur.fetchall()]


def verificar_disponibilidade_area(area: str, data: str) -> Dict[str, Any]:
    """Verifica se uma área comum está disponível em determinada data.

    Garantia 2: Retorna exclusivamente se a data está livre ou ocupada,
    sem expor quem reservou, o código da reserva ou dados de terceiros.
    """
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT COUNT(1) FROM reservas WHERE area = ? AND data = ?",
            (area, data),
        )
        ocupada = cur.fetchone()[0] > 0

    return {
        "area": area,
        "data": data,
        "disponivel": not ocupada,
        "mensagem": "Área disponível para reserva." if not ocupada else "Área já ocupada nesta data.",
    }


def reservar_area(area: str, data: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Reserva uma área comum para uma data específica.

    Garantia 1: Áreas com taxa > 0 exigem confirmação via sistema.
    Garantia 2: Apartamento obtido estritamente do estado da sessão.
    Garantia 5: Atomicidade e exclusividade garantidas no momento da gravação no SQLite.
    """
    apartamento = tool_context.state.get("apartamento", "")
    if not apartamento:
        return {"status": "erro", "mensagem": "Sessão não associada a um apartamento válido."}

    with get_db_connection() as conn:
        # 1. Valida se a área existe
        cur = conn.execute("SELECT id, nome, taxa FROM areas WHERE id = ?", (area,))
        area_row = cur.fetchone()
        if not area_row:
            return {"status": "erro", "mensagem": f"Área '{area}' não encontrada."}

        area_nome = area_row["nome"]
        taxa = float(area_row["taxa"])

        # 2. Pré-validação rápida de disponibilidade
        cur = conn.execute("SELECT COUNT(1) FROM reservas WHERE area = ? AND data = ?", (area, data))
        if cur.fetchone()[0] > 0:
            return {
                "status": "indisponivel",
                "mensagem": f"A área {area_nome} já está ocupada na data {data}.",
            }

        # 3. Garantia 1: Cobrança se taxa > 0
        if taxa > 0:
            conf = tool_context.tool_confirmation
            if conf is None:
                tool_context.request_confirmation(
                    hint=f"Reserva do {area_nome} para {data} sujeita à taxa de R$ {taxa:.2f}.",
                    payload={"acao": "reservar_area", "detalhes": {"area": area, "data": data}},
                )
                return {
                    "status": "pendente_confirmacao",
                    "mensagem": f"A reserva do {area_nome} tem taxa de R$ {taxa:.2f} e requer confirmação.",
                }
            elif not conf.confirmed:
                return {
                    "status": "cancelado",
                    "mensagem": "Reserva cancelada pois a taxa não foi confirmada.",
                }

        # 4. Gravação atômica com trava de concorrência (Garantia 5 & RN05)
        try:
            conn.execute("BEGIN IMMEDIATE")
            codigo = _gerar_codigo_reserva_unico(conn)
            conn.execute(
                "INSERT INTO codigos_reserva_usados (codigo) VALUES (?)",
                (codigo,),
            )
            conn.execute(
                "INSERT INTO reservas (codigo, apartamento, area, data) VALUES (?, ?, ?, ?)",
                (codigo, apartamento, area, data),
            )
            conn.commit()
            return {
                "status": "sucesso",
                "codigo": codigo,
                "area": area,
                "data": data,
                "mensagem": f"Reserva de {area_nome} confirmada com sucesso para {data}! Código: {codigo}",
            }
        except sqlite3.IntegrityError:
            conn.rollback()
            return {
                "status": "indisponivel",
                "mensagem": f"Não foi possível concluir a reserva: a área {area_nome} acabou de ser reservada para a data {data}.",
            }


def cancelar_minha_reserva(codigo: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Cancela uma reserva pertencente ao apartamento da sessão.

    Garantia 1: Não exige confirmação (execução direta).
    Garantia 2: Filtra exclusivamente pelo apartamento da sessão.
    """
    apartamento = tool_context.state.get("apartamento", "")
    with get_db_connection() as conn:
        cur = conn.execute(
            "DELETE FROM reservas WHERE codigo = ? AND apartamento = ?",
            (codigo, apartamento),
        )
        removidos = cur.rowcount
        conn.commit()

    if removidos == 0:
        return {
            "status": "erro",
            "mensagem": f"Reserva {codigo} não encontrada para o seu apartamento.",
        }

    return {
        "status": "sucesso",
        "mensagem": f"Reserva {codigo} cancelada com sucesso.",
    }


def listar_meus_visitantes(tool_context: ToolContext) -> List[Dict[str, Any]]:
    """Lista as autorizações de visitantes do apartamento da sessão."""
    apartamento = tool_context.state.get("apartamento", "")
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT nome, data FROM visitantes WHERE apartamento = ? ORDER BY data ASC",
            (apartamento,),
        )
        return [dict(row) for row in cur.fetchall()]


def autorizar_visitante(nome: str, data: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Autoriza a entrada de um visitante no condomínio.

    Garantia 1: Sempre exige confirmação explícita via sistema.
    Garantia 2: Apartamento obtido estritamente do estado da sessão.
    """
    apartamento = tool_context.state.get("apartamento", "")
    if not apartamento:
        return {"status": "erro", "mensagem": "Sessão não associada a um apartamento válido."}

    conf = tool_context.tool_confirmation
    if conf is None:
        tool_context.request_confirmation(
            hint=f"Autorizar entrada de {nome} no condomínio no dia {data}?",
            payload={"acao": "autorizar_visitante", "detalhes": {"nome": nome, "data": data}},
        )
        return {
            "status": "pendente_confirmacao",
            "mensagem": f"A liberação de entrada para {nome} em {data} requer confirmação formal.",
        }
    elif not conf.confirmed:
        return {
            "status": "cancelado",
            "mensagem": f"Autorização de entrada para {nome} não foi confirmada.",
        }

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO visitantes (apartamento, nome, data) VALUES (?, ?, ?)",
            (apartamento, nome, data),
        )
        conn.commit()

    return {
        "status": "sucesso",
        "nome": nome,
        "data": data,
        "mensagem": f"Entrada de {nome} autorizada para a data {data}.",
    }


def consultar_capitulo_regulamento(capitulo: int) -> str:
    """Consulta o texto de um capítulo específico do regulamento interno (1 a 14).

    Garantia 4: Retorna exclusivamente o capítulo requisitado.
    """
    return obter_capitulo(capitulo)
