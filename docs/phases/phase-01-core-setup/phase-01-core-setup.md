# Fase 01: Core Setup, SQLite & Reset CLI

## Objetivo
Configurar o ambiente virtual com `uv`, o schema relacional no SQLite com suporte a WAL mode e as operações de restauração/seed do banco de dados a partir dos arquivos imutáveis em `dados/`.

## Mapa de Dependências
- Insumos: `dados/apartamentos.json`, `dados/areas.json`, `dados/reservas.json`, `dados/visitantes.json`.
- Pré-requisitos: Python 3.12+ e `uv`.

## Step Implementations (SIs)
1. **SI-01-01**: Criar [`src/aurora/config.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/config.py) com configurações baseadas em `pydantic-settings`.
2. **SI-01-02**: Criar [`src/aurora/database.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/database.py) com DDL das tabelas (`apartamentos`, `areas`, `reservas`, `codigos_reserva_usados`, `visitantes`), ativação de WAL mode e rotinas `reset_database()` e `seed_initial_data()`.
3. **SI-01-03**: Criar [`src/aurora/cli.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/cli.py) expondo os comandos `aurora-reset` e `aurora-run`.
4. **SI-01-04**: Criar teste automatizado em [`tests/test_database.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/tests/test_database.py).

## Entregáveis e Critérios de Conclusão
- [ ] `uv run python -m aurora.cli reset` restaura o banco de dados sem erros.
- [ ] `GET` direto ao SQLite retorna os dados originais (Helena Prado no 101, RSV-1377 na quadra, Marina Duarte no 302).
- [ ] Testes de banco passam com 100% de sucesso.
