# AGENTS.md / CLAUDE.md — Residencial Aurora AI Assistant

Este documento é o ponto de entrada raiz para Agentes de IA (Google Antigravity, Claude Code, Cursor, Codex, Windsurf) trabalhando no projeto **mba-ia-desafio-criacao-agente**.

> 📌 **Aviso de Fonte Única da Verdade (Single Source of Truth)**:
> Para eliminar duplicações entre arquivos de configuração, o contexto oficial do repositório, arquitetura técnica (Google ADK + FastAPI + SQLite), regras inegociáveis de negócio, as 5 Garantias, workflows de execução e convenções estão consolidados em [`CONTEXT.md`](CONTEXT.md).
> Todos os Agentes de IA DEVEM ler [`CONTEXT.md`](CONTEXT.md) ao iniciar uma sessão ou planejar tarefas.

---

## ⚡ Comandos Rápidos e Referência

- **Instalar Dependências**: `uv sync`
- **Restaurar Estado Inicial dos Dados**: `uv run python -m aurora.cli reset`
- **Subir API HTTP**: `uv run python -m aurora.cli run` *(ou `uv run uvicorn aurora.api:app --host 0.0.0.0 --port 8000`)*
- **Executar Todos os Testes**: `uv run pytest`
- **Executar Teste Específico**: `uv run pytest tests/test_tools.py -k test_reservar_area`
- **Verificação Rápida das Rotas**:
  - `curl -s http://localhost:8000/apartamentos/101/reservas`
  - `curl -s http://localhost:8000/apartamentos/302/visitantes`

---

## 🎯 Diretivas Centrais de Execução

1. **Consultar [`CONTEXT.md`](CONTEXT.md)**: Fonte primária sobre as regras de negócio RN01-RN05, as 5 Garantias Obrigatórias, topologia multiagente e convenções de código.
2. **Política Documentation-First**: Qualquer nova funcionalidade, ajuste de regras ou refatoração deve manter os artefatos em `docs/` (`PRD.md`, `RFC.md`, `FDD.md`, `TRACKER.md` e `adrs/`) perfeitamente alinhados e rastreáveis.
3. **As 5 Garantias são Inegociáveis e Estão em Código**:
   - *Garantia 1:* Cobrança ou acesso só com confirmação via sistema (`POST /confirmacoes`).
   - *Garantia 2:* Apartamento extraído unicamente de `tool_context.state["apartamento"]`. O LLM jamais escolhe o apartamento.
   - *Garantia 3:* Nada se perde no reinício. Sessões, eventos e dados persistem em SQLite (`storage/aurora.db`).
   - *Garantia 4:* O regulamento é consultado de forma seletiva por capítulo. O agente principal nunca recebe o regulamento em suas instruções.
   - *Garantia 5:* Exclusividade atômica na escrita com `UNIQUE(area, data)` e `BEGIN IMMEDIATE` no SQLite. Concorrência simultânea responde `200 OK` amigável sem duplicidade.
4. **Execução Autônoma por Padrão**: Execute etapas, transições e testes de ponta a ponta sem pausas desnecessárias para confirmação, exceto quando houver impasses externos ou decisões humanas explícitas.
5. **Quality Gate Estrito**: Verifique a conformidade com o **Fluxo do Avaliador (Passos 1 a 15)** descrito em [`DESAFIO.md`](DESAFIO.md) e mantenha 100% de sucesso na suíte de testes.
