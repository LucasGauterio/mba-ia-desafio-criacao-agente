# Fase 03: Agentes ADK v2 & Parser do Regulamento

## Objetivo
Estruturar o parser seletivo de `dados/regulamento.md` por capítulo e a topologia multiagente com Google ADK v2:
- Agente principal `recepcao_aurora` sem regulamento no prompt.
- Sub-agents especialistas: `agente_reservas`, `agente_visitantes`, `agente_regulamento`.
- Suporte a `ResumabilityConfig(is_resumable=True)` e `DatabaseSessionService`.

Bibliotecas decididas nesta fase: ver [`library-refs.md`](library-refs.md).

## Step Implementations (SIs)
1. **SI-03-01**: Implementar [`src/aurora/regulamento.py`](../../../src/aurora/regulamento.py) com função `obter_capitulo(numero: int) -> str` e mapeamento dos 14 capítulos.
2. **SI-03-02**: Criar a tool `consultar_capitulo_regulamento(capitulo: int)`.
3. **SI-03-03**: Implementar [`src/aurora/agents.py`](../../../src/aurora/agents.py) definindo `recepcao_aurora` e os 3 especialistas com `transfer_to_agent`.
4. **SI-03-04**: Configurar o `App` e `Runner` com `DatabaseSessionService(db_url="sqlite+aiosqlite:///<DB_PATH>")`.
5. **SI-03-05**: Criar testes automatizados em [`tests/test_tools.py#L141-L150`](../../../tests/test_tools.py#L141-L150) para o parser granular do regulamento.

## Entregáveis e Critérios de Conclusão
- [x] `recepcao_aurora` não contém o regulamento na instrução — [src/aurora/agents.py#L94-L110](../../../src/aurora/agents.py#L94-L110).
- [x] 3 especialistas configurados como `sub_agents` (`agente_reservas`, `agente_visitantes`, `agente_regulamento`) — [src/aurora/agents.py#L105-L109](../../../src/aurora/agents.py#L105-L109).
- [x] `consultar_capitulo_regulamento` retorna exclusivamente o capítulo solicitado — [tests/test_tools.py#L141-L150](../../../tests/test_tools.py#L141-L150).
- [x] `criar_app()`/`criar_runner()` com `ResumabilityConfig(is_resumable=True)` e `DatabaseSessionService` executam sem erro (100% de cobertura de linha via `test_api_contract.py::test_criar_sessao_status_201`).
- **Limitação aceita**: nenhum teste envia uma mensagem real e verifica o `transfer_to_agent` de fato roteando via LLM — a topologia é construída e coberta (100% de linha), mas o roteamento real exigiria `GEMINI_API_KEY`/`GOOGLE_API_KEY`, ausente neste ambiente. Ver [`docs/decisions/technical-decisions-phase-03-adk-agents-tools.md`](../../decisions/technical-decisions-phase-03-adk-agents-tools.md).
