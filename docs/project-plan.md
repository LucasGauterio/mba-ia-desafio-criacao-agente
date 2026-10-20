# Plano Mestre de Implementação (Greenfield Project Plan) — Residencial Aurora

## 1. Sumário Executivo
Este documento define o roteiro sequencial de implementação do assistente virtual do Residencial Aurora. O projeto é desenvolvido do zero (*greenfield*), partindo unicamente dos arquivos estáticos em [`dados/`](../dados), e dividido em cinco fases atômicas orientadas a testes e validação contínua.

---

## 2. Mapa de Fases e Dependências

```mermaid
flowchart LR
    P1["Fase 01: Core Setup, SQLite & Reset CLI"] --> P2["Fase 02: Camada de Dados, Concorrência & Tools"]
    P2 --> P3["Fase 03: Agentes ADK v2 & Regulamento"]
    P3 --> P4["Fase 04: API FastAPI & Confirmações HTTP"]
    P4 --> P5["Fase 05: Suíte E2E & Fluxo do Avaliador"]
```

---

## 3. Detalhamento das Fases

### Fase 01: Core Setup, SQLite & Reset CLI
- **Objetivo**: Configurar o ambiente com `uv`, estruturar o schema relacional no SQLite com suporte a WAL mode, criar o mecanismo de seed a partir de `dados/*.json` e a CLI de reset.
- **Entregáveis**:
  - `src/aurora/config.py`: Definições de caminhos e settings Pydantic.
  - `src/aurora/database.py`: Funções `get_db_connection()`, `init_schema()`, `seed_dados()` e `reset_database()`.
  - `src/aurora/cli.py`: Entrypoints `aurora-reset` e `aurora-run`.
  - `tests/test_database.py`: Teste de integridade do reset e seeds.
- **Documentação da Fase**: [`docs/phases/phase-01-core-setup/phase-01-core-setup.md`](phases/phase-01-core-setup/phase-01-core-setup.md)

### Fase 02: Camada de Dados, Concorrência & Tools Determinísticas
- **Objetivo**: Implementar as FunctionTools em Python com as garantias determinísticas em código (taxa > 0 com confirmação, taxa 0 direta, isolamento por apartamento via state, exclusividade física com `UNIQUE(area, data)` e `BEGIN IMMEDIATE`).
- **Entregáveis**:
  - `src/aurora/tools.py`:
    - `listar_areas_comuns`
    - `consultar_minhas_reservas`
    - `verificar_disponibilidade_area`
    - `reservar_area` (Garantia 1 & 5)
    - `cancelar_minha_reserva` (Garantia 2)
    - `listar_meus_visitantes`
    - `autorizar_visitante` (Garantia 1)
  - `tests/test_tools.py`: Testes das 5 garantias isoladas nas tools.
- **Documentação da Fase**: [`docs/phases/phase-02-storage-concurrency/phase-02-storage-concurrency.md`](phases/phase-02-storage-concurrency/phase-02-storage-concurrency.md)

### Fase 03: Agentes ADK v2 & Parser do Regulamento
- **Objetivo**: Construir o parser seletivo de `dados/regulamento.md` por capítulo e montar a topologia de agentes ADK (agente principal `recepcao_aurora` + subagents `agente_reservas`, `agente_visitantes`, `agente_regulamento`) com `ResumabilityConfig(is_resumable=True)`.
- **Entregáveis**:
  - `src/aurora/regulamento.py`: Parser granular `obter_capitulo(numero: int)`.
  - `src/aurora/agents.py`: Definição de `recepcao_aurora`, especialistas, App e Runner com `DatabaseSessionService`.
  - `tests/test_regulamento.py`: Teste de extração por capítulo e isolamento de contexto.
- **Documentação da Fase**: [`docs/phases/phase-03-adk-agents-tools/phase-03-adk-agents-tools.md`](phases/phase-03-adk-agents-tools/phase-03-adk-agents-tools.md)

### Fase 04: API FastAPI & Contrato HTTP
- **Objetivo**: Expor o assistente via FastAPI em `http://localhost:8000`, implementando exatamente o contrato do `DESAFIO.md` (`POST /sessoes`, `POST /mensagens`, `POST /confirmacoes`, `GET /eventos`, `GET /verificacao`), com validação estrita de status 409 para confirmações.
- **Entregáveis**:
  - `src/aurora/api.py`: Aplicação FastAPI, rotas, schemas Pydantic, serialização assíncrona por sessão.
  - `tests/test_api_contract.py`: Teste de todos os endpoints HTTP e status codes.
- **Documentação da Fase**: [`docs/phases/phase-04-fastapi-contract/phase-04-fastapi-contract.md`](phases/phase-04-fastapi-contract/phase-04-fastapi-contract.md)

### Fase 05: Suíte E2E & Fluxo do Avaliador
- **Objetivo**: Executar a auditoria completa e teste automatizado dos 15 passos sequenciais do fluxo do avaliador contra a API real, incluindo disputa simultânea de reserva com concorrência real e reinício de servidor.
- **Entregáveis**:
  - `tests/test_evaluator_flow.py`: Automação completa dos Passos 1 a 15.
  - `docs/TRACKER.md`: Rastreabilidade final 100% preenchida.
- **Documentação da Fase**: [`docs/phases/phase-05-e2e-evaluator-validation/phase-05-e2e-evaluator-validation.md`](phases/phase-05-e2e-evaluator-validation/phase-05-e2e-evaluator-validation.md)
