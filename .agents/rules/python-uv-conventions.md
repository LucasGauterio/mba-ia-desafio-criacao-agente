# Regra: Convenções de Código Python e uv (python-uv-conventions)

## Diretivas Obrigatórias
1. **Padrões de Código**:
   - Python `>= 3.12`.
   - Tipagem estrita com Type Hints em todas as assinaturas de funções e métodos.
   - Pydantic v2 para modelos de validação de requisições e respostas HTTP.
   - Async/await nativo no FastAPI e no Google ADK (`runner.run_async`, `session_service`).
2. **Gerenciamento de Pacotes com `uv`**:
   - `pyproject.toml` como manifesto de dependências e `uv.lock` determinístico versionado.
   - Scripts de execução registrados em `[project.scripts]` (`aurora`, `aurora-reset`, `aurora-run`).
   - Todos os comandos executados via `uv run ...` para garantir o isolamento do virtualenv.
