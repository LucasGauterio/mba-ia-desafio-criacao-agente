# Referência de Bibliotecas da Fase 03

| Biblioteca | Versão (`pyproject.toml`) | Papel no SI | ADR Relacionada |
| :--- | :--- | :--- | :--- |
| `google-adk` | `==2.2.0` | SI-03-03, SI-03-04 — [`src/aurora/agents.py#L6-L8`](../../../src/aurora/agents.py#L6-L8): `Agent`, `Runner`, `App`, `ResumabilityConfig`, `DatabaseSessionService` | [ADR-001](../../adrs/ADR-001-multiagent-coordinator-specialists.md), [ADR-005](../../adrs/ADR-005-selective-regulation-retrieval.md) |
| `sqlalchemy[asyncio]` | `>=2.0.0` | SI-03-04 — motor assíncrono usado internamente por `DatabaseSessionService(db_url="sqlite+aiosqlite:///...")` | — |
| `greenlet` | `>=3.0.0` | Dependência de runtime do SQLAlchemy async (bridge sync/async) | — |
| `aiosqlite` | `>=0.20.0` | SI-03-04 — driver assíncrono do SQLite usado pelo `DatabaseSessionService` | — |
| `re` / `pathlib` (stdlib) | Builtin | SI-03-01 — [`src/aurora/regulamento.py#L3-L4`](../../../src/aurora/regulamento.py#L3-L4): parser regex por capítulo (`## Capítulo <romano>`) | — |

## Observações
- Nenhuma dessas bibliotecas foi decidida nesta fase isoladamente — todas já estavam fixadas em `pyproject.toml` desde a concepção do projeto; a Fase 03 é onde elas são efetivamente *utilizadas* pela primeira vez (`DatabaseSessionService`, `ResumabilityConfig`).
