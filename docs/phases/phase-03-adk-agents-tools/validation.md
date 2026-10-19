# Validação Arquitetural da Fase 03

- **Status**: `clean`
- **Validação de Conformidade**:
  - [x] Agente principal sem o regulamento nas instruções.
  - [x] Pelo menos 2 especialistas criados (temos 3: reservas, visitantes, regulamento).
  - [x] Parser granular do regulamento isolando capítulos.
  - [x] Sessão compatível com retomada e persistência em SQLite — reforçado pelo teste de resiliência a reinício (Passo 13) em [tests/test_api_integration.py#L196-L224](../../../tests/test_api_integration.py#L196-L224).
  - [x] Os 4 artefatos obrigatórios da fase existem: `CONTEXT.md`, `validation.md`, `library-refs.md`, `phase-03-adk-agents-tools.md`.
  - [x] SI-03-05 corrigido: apontava para `tests/test_regulamento.py` (inexistente), agora aponta para `tests/test_tools.py#L141-L150`.
- **Limitação aceita (não é pendência)**: nenhum teste automatizado verifica `transfer_to_agent` roteando de fato via LLM — documentado em [`docs/decisions/technical-decisions-phase-03-adk-agents-tools.md`](../../decisions/technical-decisions-phase-03-adk-agents-tools.md), causa raiz confirmada (ausência de `.env`/API key no ambiente), caminho de verificação manual apontado para `TEST_PLAN.md`.
