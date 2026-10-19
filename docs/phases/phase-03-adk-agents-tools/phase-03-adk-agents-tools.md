# Fase 03: Agentes ADK v2 & Parser do Regulamento

## Objetivo
Estruturar o parser seletivo de `dados/regulamento.md` por capítulo e a topologia multiagente com Google ADK v2:
- Agente principal `recepcao_aurora` sem regulamento no prompt.
- Sub-agents especialistas: `agente_reservas`, `agente_visitantes`, `agente_regulamento`.
- Suporte a `ResumabilityConfig(is_resumable=True)` e `DatabaseSessionService`.

## Step Implementations (SIs)
1. **SI-03-01**: Implementar [`src/aurora/regulamento.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/regulamento.py) com função `obter_capitulo(numero: int) -> str` e mapeamento dos 14 capítulos.
2. **SI-03-02**: Criar a tool `consultar_capitulo_regulamento(capitulo: int)`.
3. **SI-03-03**: Implementar [`src/aurora/agents.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/agents.py) definindo `recepcao_aurora` e os 3 especialistas com `transfer_to_agent`.
4. **SI-03-04**: Configurar o `App` e `Runner` com `DatabaseSessionService(db_url="sqlite+aiosqlite:///<DB_PATH>")`.
5. **SI-03-05**: Criar testes automatizados em [`tests/test_regulamento.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/tests/test_regulamento.py).
