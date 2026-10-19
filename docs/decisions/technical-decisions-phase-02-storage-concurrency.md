# Decisões Técnicas — Fase 02: Camada de Dados, Concorrência & Tools

## `BEGIN IMMEDIATE` + captura de `sqlite3.IntegrityError` para exclusividade de reserva
- **Alternativas consideradas**: lock de aplicação (`asyncio.Lock` global por área+data); lock distribuído (Redis).
- **Justificativa**: a constraint `UNIQUE(area, data)` do SQLite garante atomicidade mesmo entre processos diferentes; um lock em memória só protegeria concorrência dentro do mesmo processo Python, insuficiente se houver múltiplos workers.
- **ADR relacionada**: [ADR-002](../adrs/ADR-002-sqlite-concurrency-unique-constraint.md).

## Apartamento obtido exclusivamente de `tool_context.state`
- **Alternativas consideradas**: aceitar `apartamento` como argumento explícito da tool e validar contra a sessão.
- **Justificativa**: elimina a superfície de prompt injection — o LLM nunca decide ou sugere um apartamento; o valor vem só do estado fixado na criação da sessão.
- **ADR relacionada**: [ADR-003](../adrs/ADR-003-session-state-isolation-anti-injection.md).

## Confirmação via `tool_context.request_confirmation`/`tool_confirmation`
- **Alternativas consideradas**: pedir "confirme digitando sim" e interpretar a resposta como texto livre.
- **Justificativa**: confirmação textual é vulnerável a injeção/alucinação do LLM; o mecanismo nativo do ADK pausa a execução deterministicamente até uma resposta formal via `POST /confirmacoes`.
- **ADR relacionada**: [ADR-004](../adrs/ADR-004-tool-confirmation-lifecycle.md).
