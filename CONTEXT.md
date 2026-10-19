# CONTEXT.md — Residencial Aurora AI Assistant (Single Source of Truth)

Este documento é a **Fonte Única da Verdade** para o desenvolvimento, manutenção e validação do assistente virtual do **Residencial Aurora**.

---

## 1. Visão Geral do Projeto & Regras de Negócio

O Residencial Aurora é um condomínio que disponibiliza um assistente de IA no aplicativo dos moradores para gerenciar:
1. **Reservas de áreas comuns**: Salão de festas (taxa R$ 150), Churrasqueira (taxa R$ 80) e Quadra poliesportiva (taxa R$ 0).
2. **Cancelamento de reservas** do próprio morador.
3. **Autorização de entrada de visitantes** na portaria.
4. **Resolução de dúvidas sobre o regulamento interno** (~45 KB, 14 capítulos).

### Princípio Fundamental de Arquitetura
> *"O modelo decide o caminho, o código decide o que é permitido."*
As regras críticas de segurança, isolamento, concorrência e confirmação devem ser implementadas deterministicamente em Python e no banco SQLite, e nunca depender de instruções de prompt ou do bom comportamento do LLM.

### Regras de Negócio (RN)
- **RN01 — Exclusividade de Reserva por Área e Data**: Cada área comum aceita no máximo uma reserva por data (`AAAA-MM-DD`).
- **RN02 — Incidência de Cobrança em Reservas**:
  - `taxa > 0` (`salao-de-festas`, `churrasqueira`): gera cobrança financeira e **exige confirmação explícita do sistema**.
  - `taxa == 0` (`quadra`): não gera cobrança e **não exige confirmação** (gravação imediata).
- **RN03 — Autorização de Visitantes**: Libera acesso físico ao prédio; **sempre exige confirmação explícita do sistema**.
- **RN04 — Cancelamento de Reservas**: O morador pode cancelar apenas reservas do seu próprio apartamento, **sem confirmação pendente**.
- **RN05 — Unicidade Histórica de Códigos de Reserva**: Códigos gerados pelo sistema jamais se repetem, inclusive não reutilizando códigos de reservas já canceladas ou pré-existentes.

---

## 2. As 5 Garantias Obrigatórias em Código

| Garantia | Onde Reside no Código | Mecanismo Determinístico |
| :--- | :--- | :--- |
| **G1: Cobrança ou acesso só com confirmação** | `src/aurora/tools.py`<br>`src/aurora/api.py` | `tool_context.request_confirmation(payload=...)` pausa o ADK; a gravação só ocorre se `tool_confirmation.confirmed is True`. Rota `POST /confirmacoes` valida ID pendente na sessão e retorna `409 Conflict` se já respondido ou inexistente. |
| **G2: Cada sessão pertence a um apartamento** | `src/aurora/api.py`<br>`src/aurora/tools.py` | O apartamento é fixado na criação da sessão (`POST /sessoes`) no state do ADK (`tool_context.state["apartamento"]`). Nenhuma tool recebe `apartamento` como parâmetro vindo do LLM. Queries de disponibilidade não vazam códigos (`RSV-4821`) ou titulares. |
| **G3: Nada se perde no reinício** | `src/aurora/agents.py`<br>`src/aurora/database.py` | Sessões e eventos persistem em disco com `DatabaseSessionService` no SQLite (`storage/aurora.db`). Tabela `codigos_reserva_usados` garante unicidade perpétua mesmo após reinício ou cancelamento. |
| **G4: Regulamento consultado, não carregado** | `src/aurora/agents.py`<br>`src/aurora/regulamento.py` | Agente principal não tem o regulamento no prompt. O especialista tem apenas o sumário dos 14 capítulos e aciona a tool `consultar_capitulo_regulamento` para carregar exclusivamente o capítulo relevante, sem poluir a sessão. |
| **G5: Dois moradores, uma reserva (Concorrência)** | `src/aurora/database.py`<br>`src/aurora/tools.py` | Restrição `UNIQUE(area, data)` no SQLite. Gravação atômica com `BEGIN IMMEDIATE`. O segundo processo concorrente captura `sqlite3.IntegrityError` e retorna mensagem amigável com HTTP `200 OK` sem erro 500. |

---

## 3. Stack Tecnológica e Arquitetura Multiagente

- **Linguagem & Gerenciador**: Python 3.12+ gerenciado exclusivamente via `uv` (`pyproject.toml` e `uv.lock`).
- **Framework de Agentes**: `google-adk==2.2.0` (série 2, versão exata fixada).
- **Provedor de Modelos**: Família Gemini via Google AI Studio (`GEMINI_API_KEY` / `GOOGLE_API_KEY`).
- **Framework Web**: FastAPI com Uvicorn e suporte assíncrono.
- **Banco de Dados**: SQLite com WAL Mode (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`).
- **Topologia de Agentes**:
  - `recepcao_aurora` (Agente Principal / Triagem)
  - `agente_reservas` (Sub-agent especialista em áreas comuns)
  - `agente_visitantes` (Sub-agent especialista em portaria)
  - `agente_regulamento` (Sub-agent especialista em regulamento)

---

## 4. Contrato da API HTTP (`http://localhost:8000`)

1. `POST /sessoes` -> `{"apartamento": "101"}` -> `201 Created` `{"session_id": "..."}`
2. `POST /sessoes/{id}/mensagens` -> `{"texto": "..."}` -> `200 OK` `{"resposta": "...", "confirmacoes_pendentes": [...]}` (`404` se sessão não existir)
3. `POST /sessoes/{id}/confirmacoes` -> `{"id": "...", "confirmado": true}` -> `200 OK` (mesmo formato da rota de mensagens), `409 Conflict` (se id não for pendente), `404` (se sessão não existir)
4. `GET /sessoes/{id}/eventos` -> `200 OK` (lista cronológica completa de eventos da sessão)
5. `GET /apartamentos/{num}/reservas` -> `200 OK` (lê diretamente do SQLite, sem LLM)
6. `GET /apartamentos/{num}/visitantes` -> `200 OK` (lê diretamente do SQLite, sem LLM)

---

## 5. Estrutura de Diretórios do Projeto

```text
mba-ia-desafio-criacao-agente/
├── .agents/                    # Workspace Customizations & Rules (Antigravity)
│   ├── rules/                  # Regras inegociáveis de API e Agentes
│   └── skills/                 # Skills de execução, design-docs e validação
├── .claude/                    # Espelhamento para Claude Code CLI
│   ├── commands/               # Comandos de atalho slash
│   ├── rules/                  # Regras espelhadas
│   └── skills/                 # Skills espelhadas
├── .github/                    # Templates de PR e CI
├── dados/                      # Arquivos base imutáveis do desafio
│   ├── apartamentos.json
│   ├── areas.json
│   ├── regulamento.md
│   ├── reservas.json
│   └── visitantes.json
├── docs/                       # Documentação viva e rastreabilidade
│   ├── PRD.md                  # Requisitos de Produto e Negócio
│   ├── RFC.md                  # Proposta Técnica e Decisões de Arquitetura
│   ├── FDD.md                  # Especificação Funcional + Diagramas Mermaid
│   ├── TRACKER.md              # Matriz de Rastreabilidade Ponta a Ponta
│   ├── project-plan.md         # Plano Mestre de Implementação por Fases
│   ├── phases/                 # Planos de fases atômicos (Fases 01 a 05)
│   └── adrs/                   # Architecture Decision Records (ADR-001 a ADR-005)
├── src/aurora/                 # Código-fonte da aplicação
│   ├── __init__.py
│   ├── config.py               # Configurações Pydantic e caminhos
│   ├── database.py             # SQLite, schemas, seeds, reset e locks
│   ├── regulamento.py          # Parser e leitor granular do regulamento
│   ├── tools.py                # FunctionTools com Garantias 1, 2, 4 e 5
│   ├── agents.py               # Agentes ADK (recepcao + 3 especialistas)
│   ├── api.py                  # Endpoints FastAPI e contrato REST
│   └── cli.py                  # Entrypoints CLI (run e reset)
├── tests/                      # Bateria de testes automatizados
│   ├── conftest.py
│   ├── test_database.py        # Testes de banco, constraints e reset
│   ├── test_tools.py           # Testes das 5 garantias nas tools
│   ├── test_api_contract.py    # Testes dos endpoints HTTP e status codes
│   └── test_evaluator_flow.py  # Simulação automatizada dos 15 passos
├── AGENTS.md                   # Ponto de entrada universal de agentes
├── CLAUDE.md                   # Compatibilidade Claude Code
├── CONTEXT.md                  # Este arquivo (Single Source of Truth)
├── DESAFIO.md                  # Enunciado original do desafio
├── pyproject.toml              # Dependências e scripts uv
└── README.md                   # Entregável formal do desafio
```

---

## 6. Comandos Essenciais

```bash
# 1. Sincronizar dependências no ambiente virtual uv
uv sync

# 2. Restaurar banco de dados para o estado inicial de dados/
uv run python -m aurora.cli reset

# 3. Executar o servidor FastAPI
uv run python -m aurora.cli run

# 4. Executar suíte de testes com cobertura (pytest-cov já configurado em pyproject.toml)
uv run pytest
```
