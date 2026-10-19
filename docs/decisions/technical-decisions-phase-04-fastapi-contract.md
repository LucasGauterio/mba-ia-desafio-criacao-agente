# Decisões Técnicas — Fase 04: API FastAPI & Contrato HTTP

## `asyncio.Lock` por `session_id` para serializar requisições concorrentes
- **Alternativas consideradas**: sem lock (risco de corrida no histórico de eventos do ADK); lock global único para toda a API.
- **Justificativa**: duas requisições simultâneas na MESMA sessão poderiam corromper o histórico de eventos do ADK; um lock por sessão não impede concorrência entre sessões diferentes — necessária para o Passo 14 do avaliador (disputa concorrente entre S3 e S4).

## Validação de confirmação pendente na camada HTTP antes de encaminhar ao Runner
- **Alternativas consideradas**: sempre encaminhar ao Runner e traduzir um erro interno em `409`.
- **Justificativa**: evita gastar uma chamada ao Runner/LLM para um pedido que já se sabe inválido (ID não pendente na sessão); resposta mais rápida e previsível, e não depende do comportamento do modelo para um caso puramente determinístico.
