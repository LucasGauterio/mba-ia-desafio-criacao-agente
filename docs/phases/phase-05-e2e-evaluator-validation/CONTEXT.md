# Contexto da Fase 05: Suíte E2E & Fluxo do Avaliador

## Resumo Técnico
- Os 15 passos do avaliador são cumulativos e executam sobre o mesmo estado de banco (sem reset intermediário).
- A validação avalia eventos da sessão (`GET /sessoes/{id}/eventos`) e rotas de verificação (`GET /apartamentos/{num}/reservas` e `visitantes`).
- Apenas uma reserva pode vencer a disputa concorrente na data `2030-05-11`.
