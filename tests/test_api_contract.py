"""Testes de conformidade com o contrato REST da API FastAPI."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rotas_de_verificacao_leem_direto_do_banco(client: AsyncClient):
    """Passo 1: Confere que as rotas de verificação leem diretamente do SQLite."""
    # Apartamento 101: reserva RSV-1377 na quadra
    res_res = await client.get("/apartamentos/101/reservas")
    assert res_res.status_code == 200
    reservas_101 = res_res.json()
    assert len(reservas_101) == 1
    assert reservas_101[0]["codigo"] == "RSV-1377"
    assert reservas_101[0]["area"] == "quadra"
    assert reservas_101[0]["data"] == "2030-03-09"

    # Apartamento 302: visitante Marina Duarte
    res_vis = await client.get("/apartamentos/302/visitantes")
    assert res_vis.status_code == 200
    vis_302 = res_vis.json()
    assert len(vis_302) == 1
    assert vis_302[0]["nome"] == "Marina Duarte"
    assert vis_302[0]["data"] == "2030-03-16"


@pytest.mark.asyncio
async def test_criar_sessao_status_201(client: AsyncClient):
    """Passo 2: Confere que POST /sessoes cria a sessão e retorna 201 com session_id."""
    res = await client.post("/sessoes", json={"apartamento": "101"})
    assert res.status_code == 201
    dados = res.json()
    assert "session_id" in dados
    assert dados["session_id"] != ""


@pytest.mark.asyncio
async def test_sessao_inexistente_retorna_404(client: AsyncClient):
    """Passo 9: Confere que rotas com session_id inexistente respondem 404."""
    res_evt = await client.get("/sessoes/sessao-inexistente/eventos")
    assert res_evt.status_code == 404

    res_msg = await client.post("/sessoes/sessao-inexistente/mensagens", json={"texto": "olá"})
    assert res_msg.status_code == 404

    res_conf = await client.post(
        "/sessoes/sessao-inexistente/confirmacoes",
        json={"id": "qualquer", "confirmado": True},
    )
    assert res_conf.status_code == 404


@pytest.mark.asyncio
async def test_confirmacao_invalida_retorna_409(client: AsyncClient):
    """Passo 9: Confere que tentar confirmar um ID inexistente na sessão responde 409 Conflict."""
    res_sess = await client.post("/sessoes", json={"apartamento": "101"})
    s_id = res_sess.json()["session_id"]

    res_conf = await client.post(
        f"/sessoes/{s_id}/confirmacoes",
        json={"id": "id-inexistente", "confirmado": True},
    )
    assert res_conf.status_code == 409
    assert "Não existe confirmação pendente" in res_conf.json()["detail"]
