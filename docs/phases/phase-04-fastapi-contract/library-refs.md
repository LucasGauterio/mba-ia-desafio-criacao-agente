# Referência de Bibliotecas da Fase 04

| Biblioteca | Versão (`pyproject.toml`) | Papel no SI | ADR Relacionada |
| :--- | :--- | :--- | :--- |
| `fastapi` | `>=0.115.0` | SI-04-01 a SI-04-06 — [`src/aurora/api.py#L7`](../../../src/aurora/api.py#L7): definição do `app`, rotas e `lifespan` | [ADR-003](../../adrs/ADR-003-session-state-isolation-anti-injection.md), [ADR-004](../../adrs/ADR-004-tool-confirmation-lifecycle.md) |
| `pydantic` | `>=2.9.0` | SI-04-01 — [`src/aurora/api.py#L10`](../../../src/aurora/api.py#L10): `BaseModel` para os contratos de entrada/saída | — |
| `google-genai` (via `google-adk`) | `==2.2.0` (transitivo) | SI-04-03, SI-04-04 — [`src/aurora/api.py#L9`](../../../src/aurora/api.py#L9): `Content`, `FunctionResponse`, `Part` para enviar mensagens e respostas de confirmação ao `Runner` | — |
| `asyncio` (stdlib) | Builtin | SI-04-03, SI-04-04 — [`src/aurora/api.py#L16`](../../../src/aurora/api.py#L16): `asyncio.Lock` por sessão para serializar requisições concorrentes | [ADR-002](../../adrs/ADR-002-sqlite-concurrency-unique-constraint.md) |
| `uvicorn` | `>=0.32.0` | Servidor ASGI que expõe `app` (decidido na Fase 01, consumido aqui) | — |
| `httpx` (dev) | `>=0.27.0` | SI-04-07 — [`tests/conftest.py`](../../../tests/conftest.py): `AsyncClient` + `ASGITransport` para testar a API sem subir um servidor real | — |
| `google-adk` (`google.adk.events.Event`) | `==2.2.0` | [`tests/test_api_integration.py`](../../../tests/test_api_integration.py): construção de eventos reais do ADK para testar os caminhos de sucesso de `/mensagens`, `/confirmacoes` e `/eventos` sem chamar o LLM (mock na fronteira do `Runner.run_async`) | — |

## Observações
- `httpx.AsyncClient` com `ASGITransport` **não dispara os eventos de `lifespan`** do FastAPI por padrão; isso é mitigado porque cada rota chama `obter_runner()` diretamente (não depende exclusivamente do `lifespan` para inicializar o Runner).
