---
name: implement-phase
description: Executa a implementação sequencial dos passos de uma fase (Step Implementations) com foco em API e Agentes de IA.
---

# implement-phase: Execução de Fases de Implementação

## Diretivas de Execução
1. **Modo Autônomo por Padrão**:
   - Executar os SIs da fase em sequência, escrevendo o código em `src/aurora/` e os testes em `tests/`.
   - Não interromper o fluxo para pedir permissões triviais.
2. **Separação Rígida de Responsabilidades**:
   - `config.py`: Variáveis de ambiente e paths.
   - `database.py`: Conexão SQLite (WAL), DDL, DML e reset.
   - `regulamento.py`: Parser puro de Markdown.
   - `tools.py`: FunctionTools com as 5 garantias.
   - `agents.py`: Definição dos agentes e do App ADK.
   - `api.py`: Rotas FastAPI e contrato REST.
   - `cli.py`: Entrypoints de comando (`run`, `reset`).
3. **Validação Imediata com Testes**:
   - Ao concluir a implementação dos arquivos da fase, executar `uv run pytest` e atualizar `docs/TRACKER.md`.
