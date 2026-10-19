# Referência de Bibliotecas da Fase 02

| Biblioteca | Versão (`pyproject.toml`) | Papel no SI | ADR Relacionada |
| :--- | :--- | :--- | :--- |
| `google-adk` | `==2.2.0` | SI-02-01 a SI-02-05 — [`src/aurora/tools.py#L7`](../../../src/aurora/tools.py#L7): `ToolContext`, `tool_context.state`, `tool_context.request_confirmation`, `tool_context.tool_confirmation` | [ADR-003](../../adrs/ADR-003-session-state-isolation-anti-injection.md), [ADR-004](../../adrs/ADR-004-tool-confirmation-lifecycle.md) |
| `sqlite3` (stdlib) | Builtin Python >= 3.12 | SI-02-03 — [`src/aurora/tools.py#L109-L134`](../../../src/aurora/tools.py#L109-L134): `BEGIN IMMEDIATE` e captura de `IntegrityError` | [ADR-002](../../adrs/ADR-002-sqlite-concurrency-unique-constraint.md) |
| `random` (stdlib) | Builtin | SI-02-03 — [`src/aurora/tools.py#L13-L20`](../../../src/aurora/tools.py#L13-L20): geração de código de reserva não-repetível (RN05) | — |
| `pytest` / `pytest-asyncio` | `>=8.3.0` / `>=0.24.0` | SI-02-06 — [`tests/test_tools.py`](../../../tests/test_tools.py) | — |

## Observações
- Nenhuma biblioteca nova foi introduzida nesta fase alem do `google-adk` (já fixado desde a concepção do projeto); o diferencial da Fase 02 é o *uso* da API `ToolContext`/`request_confirmation`, não uma nova dependência.
