# Referência de Bibliotecas da Fase 01

Bibliotecas e ferramentas decididas e fixadas durante a Fase 01 (Core Setup), com o papel exato de cada uma nos Step Implementations (SIs) desta fase.

| Biblioteca | Versão (`pyproject.toml`) | Papel no SI | ADR Relacionada |
| :--- | :--- | :--- | :--- |
| `uv` | Gerenciador de ambiente/pacotes do projeto (`uv.lock` versionado) | Todos os SIs: `uv sync` provisiona o `.venv`; `uv run` executa `aurora-reset`/`aurora-run` | — |
| `hatchling` | `[build-system]` requires | Build backend do pacote `aurora` (`src/aurora`) | — |
| `pydantic-settings` | `>=2.6.0` | SI-01-01 — [`src/aurora/config.py#L4`](../../../src/aurora/config.py#L4): `Settings(BaseSettings)` carrega `.env` e expõe `AURORA_DB_PATH`, `AURORA_DADOS_DIR`, chaves de modelo | — |
| `sqlite3` (stdlib) | Builtin Python >= 3.12 | SI-01-02 — [`src/aurora/database.py#L1-L26`](../../../src/aurora/database.py#L1-L26): conexão com WAL mode, `busy_timeout`, DDL das 5 tabelas e constraint `UNIQUE(area, data)` | [ADR-002](../../adrs/ADR-002-sqlite-concurrency-unique-constraint.md) |
| `uvicorn` | `>=0.32.0` | SI-01-03 — [`src/aurora/cli.py#L17-L25`](../../../src/aurora/cli.py#L17-L25): entrypoint `aurora-run` sobe o servidor ASGI | — |
| `pytest` / `pytest-asyncio` | `>=8.3.0` / `>=0.24.0` | SI-01-04 — [`tests/test_database.py`](../../../tests/test_database.py): suíte de testes de schema, seed e constraints | — |

## Observações
- Nenhuma biblioteca externa foi introduzida para a camada de persistência: `database.py` usa exclusivamente o módulo `sqlite3` da biblioteca padrão, conforme decisão registrada em [ADR-002](../../adrs/ADR-002-sqlite-concurrency-unique-constraint.md).
- `pytest-cov` (`>=5.0.0`) foi adicionado posteriormente ao `pyproject.toml` como gate de cobertura transversal a todas as fases, não é uma decisão exclusiva da Fase 01.
