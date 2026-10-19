# Regra: Ciclo de Vida de Confirmação de Tools (tool-confirmation-lifecycle)

## Diretivas Obrigatórias (Garantia 1)
1. **Gatilhos de Confirmação**:
   - Criação de reserva em área com `taxa > 0`: OBRIGATÓRIA confirmação via sistema.
   - Autorização de visitante: OBRIGATÓRIA confirmação via sistema.
   - Criação de reserva em área com `taxa == 0` (quadra): GRAVAÇÃO DIRETA sem confirmação.
   - Cancelamento de reserva do morador: EXECUÇÃO DIRETA sem confirmação.
2. **Ciclo de Execução no ADK**:
   - Se `tool_context.tool_confirmation is None`: emitir `tool_context.request_confirmation(hint=..., payload={"acao": ..., "detalhes": {...}})` e retornar status pendente sem alterar o banco de dados.
   - Se `tool_context.tool_confirmation.confirmed is False`: abortar sem gravar no banco de dados.
   - Se `tool_context.tool_confirmation.confirmed is True`: efetivar gravação atômica no banco de dados.
3. **Validação Estrita de Estado na API (Status 409)**:
   - A rota `POST /sessoes/{id}/confirmacoes` deve verificar se o ID recebido consta na lista de confirmações ativamente pendentes na sessão.
   - Se o ID não existir ou já tiver sido respondido anteriormente, retornar IMEDIATAMENTE `409 Conflict` sem acionar o Runner.
