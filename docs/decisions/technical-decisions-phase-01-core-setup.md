# Decisões Técnicas — Fase 01: Core Setup

## Usar `sqlite3` (stdlib) síncrono para schema, seed e reset
- **Alternativas consideradas**: SQLAlchemy Core/ORM; `aiosqlite` direto.
- **Justificativa**: schema/seed/reset são operações administrativas de curta duração, chamadas fora do loop de eventos principal (CLI `aurora-reset`, `lifespan` do FastAPI). `sqlite3` síncrono simplifica o código e evita overhead assíncrono onde não há concorrência real a proteger nesta camada.
- **ADR relacionada**: nenhuma formal — decisão implícita, relacionada ao uso da mesma conexão `sqlite3` para concorrência em [ADR-002](../adrs/ADR-002-sqlite-concurrency-unique-constraint.md).

## `pydantic-settings` para configuração
- **Alternativas consideradas**: `os.environ` lido manualmente; `python-decouple`.
- **Justificativa**: tipagem e validação automática, leitura nativa de `.env`, consistente com Pydantic v2 já usado na camada HTTP (Fase 04).

## `uv` como gerenciador de pacotes/ambiente
- **Alternativas consideradas**: `pip` + `venv`; `poetry`.
- **Justificativa**: lockfile determinístico (`uv.lock`) versionado e velocidade de instalação; requisito explícito do desafio (ver `CONTEXT.md`).
