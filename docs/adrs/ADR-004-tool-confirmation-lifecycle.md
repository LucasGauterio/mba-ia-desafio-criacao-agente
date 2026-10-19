# ADR-004: Ciclo de Vida de Confirmações Human-in-the-Loop no ADK e Validação 409

## Status
Aceito (Accepted)

## Contexto
A Garantia 1 estabelece que ações geradoras de cobrança (`taxa > 0`) ou liberadoras de acesso físico (visitantes) devem ficar pendentes até a confirmação formal do morador pelo sistema via `POST /sessoes/{session_id}/confirmacoes`. A confirmação não pode vir do chat (*"já estou confirmando aqui"*), e reenviar um ID de confirmação já processado ou inexistente deve retornar HTTP `409 Conflict`.

## Decisão
1. **Pausa Nativa via `request_confirmation`**: Quando uma ação exige confirmação e `tool_context.tool_confirmation is None`, a tool invoca `tool_context.request_confirmation(...)`, gerando um evento `FunctionCall(name="adk_request_confirmation")`.
2. **Extração de Pendências na API**: A API inspeciona os eventos da sessão e extrai chamadas de confirmação que ainda não possuem resposta pareada na sessão.
3. **Validação Antecipada na Rota HTTP (Status 409)**: Antes de retomar o Runner, a rota `POST /sessoes/{id}/confirmacoes` valida se o ID consta nas confirmações abertas daquela sessão. Caso contrário, responde imediatamente com `409 Conflict`.
4. **Retomada no ADK**: Se válido, despacha um `FunctionResponse` contendo `{"confirmed": req.confirmado}`, fazendo o ADK retomar a tool no ponto em que parou.

## Consequências
- **Positivas**: Conformidade integral com o contrato REST e impedimento absoluto de execuções não autorizadas.
- **Negativas**: Exige sincronização precisa de eventos da sessão para identificar confirmações abertas.
