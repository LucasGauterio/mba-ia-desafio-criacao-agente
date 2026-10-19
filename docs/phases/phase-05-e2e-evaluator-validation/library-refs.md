# Referência de Bibliotecas da Fase 05

| Biblioteca | Versão (`pyproject.toml`) | Papel no SI | ADR Relacionada |
| :--- | :--- | :--- | :--- |
| `pytest-asyncio` | `>=0.24.0` | SI-05-01, SI-05-02 — execução de testes assíncronos (`@pytest.mark.asyncio`) | — |
| `httpx` | `>=0.27.0` | SI-05-01 — `AsyncClient` para simular chamadas HTTP nos testes de contrato | — |
| `unittest.mock` (stdlib) | Builtin | SI-05-01 — [`tests/test_evaluator_flow.py#L4`](../../../tests/test_evaluator_flow.py#L4): `MagicMock` para simular `tool_context` sem passar pela API real | — |
| `asyncio` (stdlib) | Builtin | SI-05-02 — [`tests/test_evaluator_flow.py#L3,#L118-L122`](../../../tests/test_evaluator_flow.py#L118): `asyncio.gather` + `loop.run_in_executor` para disputa concorrente (Passo 14) | [ADR-002](../../adrs/ADR-002-sqlite-concurrency-unique-constraint.md) |
| `pytest-cov` | `>=5.0.0` | Gate de cobertura transversal usado para auditar esta própria fase (ver achados de cobertura em `validation.md`) | — |
| `google-adk` (`google.adk.events.Event`) | `==2.2.0` | [`tests/test_api_integration.py`](../../../tests/test_api_integration.py): Passos 12 e 13 mockam a fronteira do `Runner` com eventos reais do ADK em vez de `tool_context` mockado | — |

## Observações
- Nenhuma biblioteca nova foi decidida nesta fase; o uso de `MagicMock` em vez de uma chamada real ao `Runner`/LLM é a causa raiz dos gaps registrados em `validation.md` (passos 11, 12 e 13 sem cobertura real de integração).
