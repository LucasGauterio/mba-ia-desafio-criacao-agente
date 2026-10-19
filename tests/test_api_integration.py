"""Testes de integração que exercitam os caminhos de sucesso da API.

Mockam apenas a fronteira do Runner (`run_async`), construindo objetos reais
`google.adk.events.Event` e persistindo-os via `session_service.append_event`.
Não dependem de rede nem de GEMINI_API_KEY/GOOGLE_API_KEY — o objetivo é provar
que a camada FastAPI (extração de confirmações, serialização, ciclo 409) funciona
quando o Runner/LLM produz os eventos esperados, não que o LLM de fato os produz.
"""

import pytest
from google.adk.events import Event
from google.genai.types import Content, FunctionCall, FunctionResponse, Part
from httpx import AsyncClient

from aurora import api as api_module
from aurora.agents import criar_runner
from aurora.database import get_db_connection
from aurora.tools import consultar_capitulo_regulamento


@pytest.mark.asyncio
async def test_post_mensagens_sucesso_extrai_confirmacao_pendente(client: AsyncClient, monkeypatch):
    """SI-04-03: POST /mensagens processa a resposta do Runner e extrai confirmacoes_pendentes."""
    runner = api_module.obter_runner()
    res_sessao = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = res_sessao.json()["session_id"]
    session = await api_module.obter_sessao_por_id(runner, session_id)

    evt = Event(
        author="agente_reservas",
        content=Content(
            role="model",
            parts=[
                Part(
                    function_call=FunctionCall(
                        id="call-res-1",
                        name="adk_request_confirmation",
                        args={
                            "payload": {
                                "acao": "reservar_area",
                                "detalhes": {"area": "salao-de-festas", "data": "2030-06-01"},
                            }
                        },
                    )
                )
            ],
        ),
    )

    async def fake_run_async(*, user_id, session_id, new_message):
        await runner.session_service.append_event(session, evt)
        yield evt

    monkeypatch.setattr(runner, "run_async", fake_run_async)

    res = await client.post(f"/sessoes/{session_id}/mensagens", json={"texto": "quero reservar o salão de festas"})
    assert res.status_code == 200
    body = res.json()
    assert len(body["confirmacoes_pendentes"]) == 1
    pendente = body["confirmacoes_pendentes"][0]
    assert pendente["id"] == "call-res-1"
    assert pendente["acao"] == "reservar_area"
    assert pendente["detalhes"] == {"area": "salao-de-festas", "data": "2030-06-01"}


@pytest.mark.asyncio
async def test_post_confirmacoes_aprovacao_finaliza_pendencia_e_bloqueia_repeticao(
    client: AsyncClient, monkeypatch
):
    """SI-04-04: POST /confirmacoes com confirmado=true processa a aprovação; reenviar o
    mesmo id depois disso retorna 409 (já respondida)."""
    runner = api_module.obter_runner()
    res_sessao = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = res_sessao.json()["session_id"]
    session = await api_module.obter_sessao_por_id(runner, session_id)

    evt_pedido = Event(
        author="agente_reservas",
        content=Content(
            role="model",
            parts=[
                Part(
                    function_call=FunctionCall(
                        id="call-res-2",
                        name="adk_request_confirmation",
                        args={
                            "payload": {
                                "acao": "reservar_area",
                                "detalhes": {"area": "churrasqueira", "data": "2030-06-02"},
                            }
                        },
                    )
                )
            ],
        ),
    )

    async def fake_run_async_pedido(*, user_id, session_id, new_message):
        await runner.session_service.append_event(session, evt_pedido)
        yield evt_pedido

    monkeypatch.setattr(runner, "run_async", fake_run_async_pedido)
    res1 = await client.post(f"/sessoes/{session_id}/mensagens", json={"texto": "quero reservar a churrasqueira"})
    assert res1.status_code == 200
    assert len(res1.json()["confirmacoes_pendentes"]) == 1

    evt_resposta = Event(
        author="agente_reservas",
        content=Content(
            role="user",
            parts=[
                Part(
                    function_response=FunctionResponse(
                        id="call-res-2",
                        name="adk_request_confirmation",
                        response={"confirmed": True},
                    )
                )
            ],
        ),
    )
    evt_texto = Event(
        author="agente_reservas",
        content=Content(role="model", parts=[Part(text="Reserva da churrasqueira confirmada com sucesso!")]),
    )

    async def fake_run_async_aprovacao(*, user_id, session_id, new_message):
        for evt in (evt_resposta, evt_texto):
            await runner.session_service.append_event(session, evt)
            yield evt

    monkeypatch.setattr(runner, "run_async", fake_run_async_aprovacao)
    res2 = await client.post(f"/sessoes/{session_id}/confirmacoes", json={"id": "call-res-2", "confirmado": True})
    assert res2.status_code == 200
    body2 = res2.json()
    assert body2["confirmacoes_pendentes"] == []
    assert "confirmada" in body2["resposta"].lower()

    res3 = await client.post(f"/sessoes/{session_id}/confirmacoes", json={"id": "call-res-2", "confirmado": True})
    assert res3.status_code == 409


@pytest.mark.asyncio
async def test_get_eventos_retorna_conteudo_completo_da_sessao(client: AsyncClient):
    """SI-04-05: GET /eventos retorna a lista cronológica completa com conteúdo."""
    runner = api_module.obter_runner()
    res_sessao = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = res_sessao.json()["session_id"]
    session = await api_module.obter_sessao_por_id(runner, session_id)

    evt = Event(author="user", content=Content(role="user", parts=[Part(text="Olá, assistente!")]))
    await runner.session_service.append_event(session, evt)

    res = await client.get(f"/sessoes/{session_id}/eventos")
    assert res.status_code == 200
    eventos = res.json()
    assert len(eventos) >= 1
    assert any("Olá, assistente!" in str(e) for e in eventos)


@pytest.mark.asyncio
async def test_passo_12_consulta_seletiva_do_regulamento_sem_vazar_outros_capitulos(
    client: AsyncClient, monkeypatch
):
    """Passo 12: a resposta e os eventos da sessão contêm apenas o capítulo consultado (Piscina)."""
    runner = api_module.obter_runner()
    res_sessao = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = res_sessao.json()["session_id"]
    session = await api_module.obter_sessao_por_id(runner, session_id)

    texto_capitulo_4 = consultar_capitulo_regulamento(4)
    assert "Capítulo IV" in texto_capitulo_4

    eventos = [
        Event(
            author="agente_regulamento",
            content=Content(
                role="model",
                parts=[
                    Part(
                        function_call=FunctionCall(
                            id="call-reg-1", name="consultar_capitulo_regulamento", args={"capitulo": 4}
                        )
                    )
                ],
            ),
        ),
        Event(
            author="agente_regulamento",
            content=Content(
                role="user",
                parts=[
                    Part(
                        function_response=FunctionResponse(
                            id="call-reg-1",
                            name="consultar_capitulo_regulamento",
                            response={"result": texto_capitulo_4},
                        )
                    )
                ],
            ),
        ),
        Event(
            author="agente_regulamento",
            content=Content(
                role="model",
                parts=[Part(text="A piscina fecha às 20h aos domingos, conforme o Capítulo IV do regulamento.")],
            ),
        ),
    ]

    async def fake_run_async(*, user_id, session_id, new_message):
        for evt in eventos:
            await runner.session_service.append_event(session, evt)
            yield evt

    monkeypatch.setattr(runner, "run_async", fake_run_async)

    res = await client.post(
        f"/sessoes/{session_id}/mensagens", json={"texto": "A piscina fecha que horas no domingo?"}
    )
    assert res.status_code == 200
    assert "20h" in res.json()["resposta"]

    res_eventos = await client.get(f"/sessoes/{session_id}/eventos")
    assert res_eventos.status_code == 200
    conteudo = str(res_eventos.json())
    assert "Capítulo IV" in conteudo
    for capitulo_proibido in ["Capítulo VIII", "Capítulo IX", "Animais de estimação", "Mudanças"]:
        assert capitulo_proibido not in conteudo


@pytest.mark.asyncio
async def test_passo_13_resiliencia_a_reinicio_sem_reset(client: AsyncClient):
    """Passo 13 / Garantia 3: sessão e dados persistem ao recriar o Runner sobre o mesmo banco,
    sem chamar reset_database()."""
    res_sessao = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = res_sessao.json()["session_id"]

    runner_antigo = api_module.obter_runner()
    sessao_antes = await api_module.obter_sessao_por_id(runner_antigo, session_id)
    marcador = Event(
        author="user",
        content=Content(role="user", parts=[Part(text="Mensagem antes do reinício simulado.")]),
    )
    await runner_antigo.session_service.append_event(sessao_antes, marcador)

    # "Reinício": nova instância de Runner/DatabaseSessionService sobre o MESMO arquivo de banco.
    runner_novo = criar_runner()
    sessao_depois = await runner_novo.session_service.get_session(
        app_name="aurora", user_id="101", session_id=session_id
    )

    assert sessao_depois is not None
    assert sessao_depois.state.get("apartamento") == "101"
    assert any(
        p.text == "Mensagem antes do reinício simulado."
        for evt in sessao_depois.events
        for p in (evt.content.parts if evt.content and evt.content.parts else [])
    )

    # Dados de domínio também sobrevivem ao "reinício" (RSV-1377 continua no 101).
    with get_db_connection() as conn:
        cur = conn.execute("SELECT 1 FROM reservas WHERE codigo = 'RSV-1377' AND apartamento = '101'")
        assert cur.fetchone() is not None
