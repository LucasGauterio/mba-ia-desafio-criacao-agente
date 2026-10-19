# Decisões Técnicas — Fase 03: Agentes ADK v2 & Parser do Regulamento

## Topologia coordenador + especialistas
- **Alternativas consideradas**: agente único monolítico com todas as 8 tools e uma instrução gigante.
- **Justificativa**: isola o contexto de cada domínio (reservas, visitantes, regulamento); evita que o agente principal receba o regulamento inteiro nas instruções (Garantia 4) e reduz a chance de confusão entre tools de domínios diferentes.
- **ADR relacionada**: [ADR-001](../adrs/ADR-001-multiagent-coordinator-specialists.md).

## Regulamento consultado via tool `consultar_capitulo_regulamento` (parser por capítulo)
- **Alternativas consideradas**: RAG com embeddings; regulamento completo no system prompt.
- **Justificativa**: ~45 KB excede o que deveria viver em uma instrução de agente; um parser determinístico por capítulo é mais simples que RAG e garante que nenhum capítulo não solicitado apareça na resposta ou nos eventos da sessão.
- **ADR relacionada**: [ADR-005](../adrs/ADR-005-selective-regulation-retrieval.md).

## `DatabaseSessionService` (SQLAlchemy async / `aiosqlite`) em vez de `InMemorySessionService`
- **Alternativas consideradas**: `InMemorySessionService` (padrão do ADK); Redis.
- **Justificativa**: Garantia 3 exige que nada se perca no reinício; sessão em memória não sobrevive a um restart do processo.

## Limitação aceita: roteamento real via `transfer_to_agent` não é verificado em teste automatizado
- **Causa**: não há `GEMINI_API_KEY`/`GOOGLE_API_KEY` configurada neste ambiente — confirmado: o arquivo `.env` não existe no repositório. Chamar o LLM real exigiria rede e credenciais indisponíveis no ambiente de desenvolvimento/CI padrão.
- **Mitigação**: a construção da topologia (`criar_app()`/`criar_runner()`, `sub_agents`) é verificada estruturalmente (100% de cobertura de linha via `test_api_contract.py::test_criar_sessao_status_201`). O comportamento real de roteamento do LLM é verificado manualmente via `TEST_PLAN.md` (curl) quando uma chave de API estiver configurada.
