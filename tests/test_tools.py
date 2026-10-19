"""Testes unitários das tools e validação determinística das 5 garantias."""

from unittest.mock import MagicMock

from aurora.database import get_db_connection
from aurora.tools import (
    autorizar_visitante,
    cancelar_minha_reserva,
    consultar_capitulo_regulamento,
    consultar_minhas_reservas,
    listar_areas_comuns,
    listar_meus_visitantes,
    reservar_area,
    verificar_disponibilidade_area,
)


def test_verificar_disponibilidade_sem_vazamento_de_dados():
    """Garantia 2: Checar disponibilidade informa apenas boolean sem expor titulares alheios."""
    # O salão está ocupado em 2030-03-16 pelo apartamento 302 (RSV-4821)
    res = verificar_disponibilidade_area("salao-de-festas", "2030-03-16")
    assert res["disponivel"] is False
    assert "RSV-4821" not in str(res)
    assert "302" not in str(res)
    assert "Rafael" not in str(res)


def test_reservar_area_sem_taxa_executa_direto():
    """RN02 / Garantia 1: Área com taxa zero (quadra) grava imediatamente sem pedir confirmação."""
    ctx = MagicMock()
    ctx.state = {"apartamento": "101"}
    ctx.tool_confirmation = None

    res = reservar_area("quadra", "2030-04-06", ctx)
    ctx.request_confirmation.assert_not_called()
    assert res["status"] == "sucesso"
    assert res["codigo"].startswith("RSV-")

    # Verifica se foi gravado no banco
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE codigo = ?", (res["codigo"],))
        gravado = cur.fetchone()
        assert gravado is not None
        assert gravado["apartamento"] == "101"
        assert gravado["area"] == "quadra"


def test_reservar_area_com_taxa_requer_confirmacao_e_cancela_se_rejeitado():
    """RN02 / Garantia 1: Área com taxa maior que zero exige confirmação formal."""
    ctx = MagicMock()
    ctx.state = {"apartamento": "101"}
    ctx.tool_confirmation = None

    # 1. Primeira chamada -> deve pausar e pedir confirmação
    res_pendente = reservar_area("salao-de-festas", "2030-04-20", ctx)
    ctx.request_confirmation.assert_called_once()
    assert res_pendente["status"] == "pendente_confirmacao"

    # Confere que nada foi gravado no banco ainda
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE area = 'salao-de-festas' AND data = '2030-04-20'")
        assert cur.fetchone() is None

    # 2. Resposta com confirmed = False -> cancela sem gravar
    ctx_negado = MagicMock()
    ctx_negado.state = {"apartamento": "101"}
    ctx_negado.tool_confirmation = MagicMock(confirmed=False)
    res_negado = reservar_area("salao-de-festas", "2030-04-20", ctx_negado)
    assert res_negado["status"] == "cancelado"

    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE area = 'salao-de-festas' AND data = '2030-04-20'")
        assert cur.fetchone() is None


def test_reservar_area_com_taxa_grava_quando_confirmado():
    """RN02 / Garantia 1: Grava exatamente após confirmação positiva."""
    ctx = MagicMock()
    ctx.state = {"apartamento": "101"}
    ctx.tool_confirmation = MagicMock(confirmed=True)

    res = reservar_area("salao-de-festas", "2030-04-20", ctx)
    assert res["status"] == "sucesso"
    assert res["codigo"].startswith("RSV-")

    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE codigo = ?", (res["codigo"],))
        assert cur.fetchone() is not None


def test_cancelar_minha_reserva_e_protecao_alheia():
    """RN04 & Garantia 2: Morador cancela apenas a própria reserva sem confirmação."""
    ctx_101 = MagicMock()
    ctx_101.state = {"apartamento": "101"}

    # 1. Morador do 101 tenta cancelar RSV-4821 (que pertence ao 302)
    res_erro = cancelar_minha_reserva("RSV-4821", ctx_101)
    assert res_erro["status"] == "erro"

    # Confere que a reserva do 302 CONTINUA intacta no banco
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE codigo = 'RSV-4821'")
        reserva_302 = cur.fetchone()
        assert reserva_302 is not None
        assert reserva_302["apartamento"] == "302"

    # 2. Morador do 101 cancela sua própria reserva RSV-1377
    res_sucesso = cancelar_minha_reserva("RSV-1377", ctx_101)
    assert res_sucesso["status"] == "sucesso"

    # Confere que foi removida
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE codigo = 'RSV-1377'")
        assert cur.fetchone() is None


def test_autorizar_visitante_fluxo_confirmacao():
    """RN03 & Garantia 1: Autorizar visitante sempre exige confirmação formal."""
    ctx = MagicMock()
    ctx.state = {"apartamento": "101"}
    ctx.tool_confirmation = None

    # 1. Pede confirmação
    res_pendente = autorizar_visitante("Joana Ribeiro", "2030-04-21", ctx)
    ctx.request_confirmation.assert_called_once()
    assert res_pendente["status"] == "pendente_confirmacao"

    # 2. Grava após confirmação
    ctx_aprovado = MagicMock()
    ctx_aprovado.state = {"apartamento": "101"}
    ctx_aprovado.tool_confirmation = MagicMock(confirmed=True)

    res_ok = autorizar_visitante("Joana Ribeiro", "2030-04-21", ctx_aprovado)
    assert res_ok["status"] == "sucesso"

    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM visitantes WHERE apartamento = '101' AND nome = 'Joana Ribeiro'")
        assert cur.fetchone() is not None


def test_consultar_capitulo_regulamento_granular():
    """Garantia 4: Consulta de regulamento retorna apenas o capítulo solicitado."""
    # Capítulo 4: Piscina
    cap4 = consultar_capitulo_regulamento(4)
    assert "Capítulo IV: Piscina" in cap4
    assert "Art. 22" in cap4
    assert "20h" in cap4  # fecha às 20h aos domingos
    # Não deve conter animais de estimação (Capítulo VIII) nem mudanças (Capítulo IX)
    assert "Capítulo VIII" not in cap4
    assert "Capítulo IX" not in cap4
