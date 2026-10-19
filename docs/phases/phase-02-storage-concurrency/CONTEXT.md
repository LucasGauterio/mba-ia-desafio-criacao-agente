# Contexto da Fase 02: Camada de Dados, Concorrência & Tools Determinísticas

## Resumo Técnico
- Nenhuma tool recebe o parâmetro `apartamento` vindo do modelo LLM.
- O apartamento é obtido exclusivamente de `tool_context.state["apartamento"]`.
- `reservar_area` verifica a taxa da área: se `taxa == 0` (`quadra`), grava diretamente sem chamar `request_confirmation`; se `taxa > 0`, chama `tool_context.request_confirmation(...)` se `tool_confirmation is None`.
- `autorizar_visitante` sempre chama `request_confirmation` com `detalhes: {"nome": nome, "data": data}`.
- O cancelamento é restrito a `WHERE codigo = ? AND apartamento = ?` e executa sem confirmação.
