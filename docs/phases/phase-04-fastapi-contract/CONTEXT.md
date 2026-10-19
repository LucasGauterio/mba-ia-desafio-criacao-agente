# Contexto da Fase 04: API FastAPI & Contrato HTTP

## Resumo Técnico
- Rotas recebem e retornam exclusivamente JSON.
- Sessões inexistentes retornam `404 Not Found` em todas as rotas com `{session_id}`.
- Confirmações inválidas ou repetidas retornam `409 Conflict`.
- Rotas de verificação leem diretamente do SQLite sem passar pelo LLM.
