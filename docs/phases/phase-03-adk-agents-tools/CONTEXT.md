# Contexto da Fase 03: Agentes ADK v2 & Parser do Regulamento

## Resumo Técnico
- O regulamento completo tem ~45 KB e 14 capítulos.
- Se o regulamento entrar nas instruções do agente principal ou no histórico geral, estoura tokens e vaza informações.
- A tool `consultar_capitulo_regulamento` lê e retorna apenas o capítulo solicitado, de modo que os eventos de sessão de `GET /eventos` registram apenas o capítulo em questão (ex: Cap. IV sobre Piscina).
- O `App` utiliza `ResumabilityConfig(is_resumable=True)` para permitir que confirmações pendentes sejam retomadas sem perda de contexto ou do subagente de origem.
