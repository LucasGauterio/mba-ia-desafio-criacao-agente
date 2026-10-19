"""Testes unitários e de integridade da camada de banco de dados SQLite."""

import sqlite3
import pytest

from aurora.database import get_db_connection, reset_database


def test_schema_e_seed_inicial():
    """Valida se o seed carrega com precisão os 6 apartamentos, 3 áreas, 3 reservas e 2 visitantes."""
    with get_db_connection() as conn:
        aptos = conn.execute("SELECT numero, morador FROM apartamentos ORDER BY numero").fetchall()
        assert len(aptos) == 6
        assert aptos[0]["numero"] == "101"
        assert aptos[0]["morador"] == "Helena Prado"

        areas = conn.execute("SELECT id, taxa FROM areas ORDER BY id").fetchall()
        assert len(areas) == 3
        areas_dict = {a["id"]: a["taxa"] for a in areas}
        assert areas_dict["quadra"] == 0.0
        assert areas_dict["churrasqueira"] == 80.0
        assert areas_dict["salao-de-festas"] == 150.0

        reservas = conn.execute("SELECT codigo, apartamento, area, data FROM reservas ORDER BY codigo").fetchall()
        assert len(reservas) == 3
        codigos = {r["codigo"] for r in reservas}
        assert "RSV-1377" in codigos
        assert "RSV-4821" in codigos
        assert "RSV-2950" in codigos

        visitantes = conn.execute("SELECT apartamento, nome, data FROM visitantes").fetchall()
        assert len(visitantes) == 2
        nomes = {v["nome"] for v in visitantes}
        assert "Marina Duarte" in nomes
        assert "Paulo Nogueira" in nomes


def test_exclusividade_reserva_unique_constraint():
    """Garantia 5: Testa a colisão atômica da constraint UNIQUE(area, data) no SQLite."""
    with get_db_connection() as conn:
        # A quadra já está reservada para 2030-03-09 (RSV-1377)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO reservas (codigo, apartamento, area, data) VALUES (?, ?, ?, ?)",
                ("RSV-9999", "201", "quadra", "2030-03-09"),
            )


def test_historico_codigos_reserva_usados():
    """RN05: Testa que a tabela de códigos usados preserva os códigos mesmo após cancelamento."""
    with get_db_connection() as conn:
        # Cancela a reserva RSV-1377
        conn.execute("DELETE FROM reservas WHERE codigo = 'RSV-1377'")
        conn.commit()

        # Confere que não existe mais em reservas
        cur = conn.execute("SELECT 1 FROM reservas WHERE codigo = 'RSV-1377'")
        assert cur.fetchone() is None

        # Mas continua registrada em codigos_reserva_usados
        cur = conn.execute("SELECT 1 FROM codigos_reserva_usados WHERE codigo = 'RSV-1377'")
        assert cur.fetchone() is not None
