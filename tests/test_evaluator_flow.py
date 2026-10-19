"""Teste de integração ponta a ponta simulando as verificações do fluxo do avaliador."""

import asyncio
from unittest.mock import MagicMock
import pytest
from httpx import AsyncClient

from aurora.database import get_db_connection
from aurora.tools import cancelar_minha_reserva, reservar_area, verificar_disponibilidade_area


@pytest.mark.asyncio
async def test_passo_1_estado_inicial_e_rotas_de_verificacao(client: AsyncClient):
    """Passo 1: Confere que GET /apartamentos/101/reservas lista RSV-1377 e 302 lista Marina Duarte."""
    r_101 = await client.get("/apartamentos/101/reservas")
    assert r_101.status_code == 200
    res_101 = r_101.json()
    assert any(r["codigo"] == "RSV-1377" and r["area"] == "quadra" for r in res_101)

    v_302 = await client.get("/apartamentos/302/visitantes")
    assert v_302.status_code == 200
    vis_302 = v_302.json()
    assert any(v["nome"] == "Marina Duarte" and v["data"] == "2030-03-16" for v in vis_302)


@pytest.mark.asyncio
async def test_passo_2_criacao_sessao(client: AsyncClient):
    """Passo 2: POST /sessoes com 101 devolve 201 e session_id."""
    res = await client.post("/sessoes", json={"apartamento": "101"})
    assert res.status_code == 201
    assert "session_id" in res.json()


def test_passo_3_e_4_isolamento_de_sessao_e_tentativa_de_cancelamento_alheio():
    """Passos 3 e 4: Morador do 101 não consegue cancelar nem vazar dados do 302."""
    ctx_101 = MagicMock()
    ctx_101.state = {"apartamento": "101"}

    # Passo 4: Tentar cancelar a reserva do 302 (RSV-4821 em 2030-03-16)
    res_cancel = cancelar_minha_reserva("RSV-4821", ctx_101)
    assert res_cancel["status"] == "erro"

    # Confere que a reserva do 302 permanece intacta
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE codigo = 'RSV-4821' AND apartamento = '302'")
        assert cur.fetchone() is not None


def test_passo_5_cancelamento_proprio_sem_confirmacao():
    """Passo 5: Cancelar a própria reserva da quadra em 2030-03-09."""
    ctx_101 = MagicMock()
    ctx_101.state = {"apartamento": "101"}

    res = cancelar_minha_reserva("RSV-1377", ctx_101)
    assert res["status"] == "sucesso"

    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM reservas WHERE codigo = 'RSV-1377'")
        assert cur.fetchone() is None


def test_passo_6_reserva_taxa_zero_sem_confirmacao():
    """Passo 6: Reservar a quadra para 2030-04-06 sem confirmação pendente."""
    ctx_101 = MagicMock()
    ctx_101.state = {"apartamento": "101"}
    ctx_101.tool_confirmation = None

    res = reservar_area("quadra", "2030-04-06", ctx_101)
    ctx_101.request_confirmation.assert_not_called()
    assert res["status"] == "sucesso"


def test_passo_7_e_8_reserva_com_cobranca_negacao_e_aprovacao():
    """Passos 7 e 8: Reservar salão para 2030-04-20 com negação e aprovação."""
    ctx_101 = MagicMock()
    ctx_101.state = {"apartamento": "101"}
    ctx_101.tool_confirmation = None

    # Passo 7: Gera confirmação
    res_p = reservar_area("salao-de-festas", "2030-04-20", ctx_101)
    assert res_p["status"] == "pendente_confirmacao"

    # Negação
    ctx_neg = MagicMock()
    ctx_neg.state = {"apartamento": "101"}
    ctx_neg.tool_confirmation = MagicMock(confirmed=False)
    res_neg = reservar_area("salao-de-festas", "2030-04-20", ctx_neg)
    assert res_neg["status"] == "cancelado"

    # Passo 8: Aprovação
    ctx_aprov = MagicMock()
    ctx_aprov.state = {"apartamento": "101"}
    ctx_aprov.tool_confirmation = MagicMock(confirmed=True)
    res_aprov = reservar_area("salao-de-festas", "2030-04-20", ctx_aprov)
    assert res_aprov["status"] == "sucesso"


def test_passo_10_reserva_em_data_ocupada_sem_vazamento():
    """Passo 10: Tentar reservar data ocupada pelo 302 sem vazar RSV-4821 nem 302."""
    disp = verificar_disponibilidade_area("salao-de-festas", "2030-03-16")
    assert disp["disponivel"] is False
    assert "RSV-4821" not in str(disp)
    assert "302" not in str(disp)


@pytest.mark.asyncio
async def test_passo_14_disputa_concorrente_simultanea():
    """Passo 14: Disputa simultânea de dois moradores pela mesma área e data."""
    ctx_s3 = MagicMock()
    ctx_s3.state = {"apartamento": "101"}
    ctx_s3.tool_confirmation = MagicMock(confirmed=True)

    ctx_s4 = MagicMock()
    ctx_s4.state = {"apartamento": "201"}
    ctx_s4.tool_confirmation = MagicMock(confirmed=True)

    # Dispara duas aprovações assíncronas concorrentes para a mesma área e data
    loop = asyncio.get_running_loop()
    res1, res2 = await asyncio.gather(
        loop.run_in_executor(None, reservar_area, "salao-de-festas", "2030-05-11", ctx_s3),
        loop.run_in_executor(None, reservar_area, "salao-de-festas", "2030-05-11", ctx_s4),
    )

    statuses = [res1["status"], res2["status"]]
    # Exatamente uma vitoriosa e uma recusada com status indisponível
    assert "sucesso" in statuses
    assert "indisponivel" in statuses

    # Verifica no banco de dados que existe rigorosamente apenas UMA reserva para 2030-05-11
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT COUNT(1) FROM reservas WHERE area = 'salao-de-festas' AND data = '2030-05-11'"
        )
        total = cur.fetchone()[0]
        assert total == 1
