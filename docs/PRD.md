# PRD: Assistente Virtual do Residencial Aurora

## 1. Visão Geral e Contexto
O **Residencial Aurora** é um condomínio residencial que busca automatizar o atendimento aos moradores por meio de um assistente conversacional integrado ao aplicativo móvel.

### Problema de Negócio
Em sistemas conversacionais baseados puramente em LLMs, mensagens maliciosas ou confusas de moradores podem contornar regras críticas de negócio (prompt injection, cancelamento indevido, burla de taxas, liberação de estranhos). A síndica do condomínio impôs uma exigência inegociável: **o assistente jamais pode ser convencido a quebrar uma regra**, e situações de concorrência ou reinício não podem provocar inconsistências.

---

## 2. Regras de Negócio Inegociáveis (RN)
- **RN01**: Cada área comum aceita no máximo uma reserva por data (`AAAA-MM-DD`).
- **RN02**: Reservar área com `taxa > 0` gera cobrança e exige confirmação formal. Área com `taxa == 0` não gera cobrança e não pede confirmação.
- **RN03**: Autorizar visitante libera acesso físico ao condomínio e sempre exige confirmação formal.
- **RN04**: O morador pode cancelar apenas reservas pertencentes ao seu próprio apartamento, sem confirmação.
- **RN05**: O código de uma reserva nova é único, gerado pelo sistema e nunca repete outro código histórico, mesmo de reservas canceladas.

---

## 3. As 5 Garantias Críticas do Condomínio
1. **Garantia 1 (Confirmação Prévia)**: Nenhuma cobrança ou liberação de acesso físico é efetivada antes da resposta via rota HTTP de confirmações. Confirmações no chat não têm validade. Reenvio ou ID inexistente recebe `409 Conflict`.
2. **Garantia 2 (Isolamento de Sessão)**: O apartamento é imutável por sessão. Nenhuma tool aceita apartamento vindo do LLM. Respostas e eventos nunca revelam dados de terceiros.
3. **Garantia 3 (Persistência e Sobrevivência)**: Reiniciar o servidor não perde sessões, histórico, reservas ou visitantes.
4. **Garantia 4 (Consulta Granular do Regulamento)**: O regulamento é consultado por capítulo via tool; o agente principal não possui o regulamento no prompt e os eventos da sessão não contêm capítulos alheios.
5. **Garantia 5 (Exclusividade Concorrente)**: Disputas simultâneas pela mesma área e data resultam em exatamente uma reserva ativa e ambas as requisições recebem `200 OK`.

---

## 4. Requisitos Funcionais (RF)
- **RF01 (Gestão de Sessão)**: Inicialização da sessão associada ao apartamento autenticado (`POST /sessoes`).
- **RF02 (Conversação Interativa)**: Envio de mensagens em linguagem natural com suporte a transferências entre especialistas (`POST /sessoes/{id}/mensagens`).
- **RF03 (Resolução de Confirmações)**: Endpoint dedicado para aprovação ou rejeição de ações pendentes (`POST /sessoes/{id}/confirmacoes`).
- **RF04 (Auditoria de Eventos)**: Consulta à lista cronológica e completa de eventos gravados pelo runtime (`GET /sessoes/{id}/eventos`).
- **RF05 (Verificação Administrativa)**: Endpoints de verificação direta no banco sem passar pelo LLM (`GET /apartamentos/{num}/reservas` e `visitantes`).

---

## 5. Fora de Escopo
- Interface visual / frontend (a entrega é estritamente a API HTTP).
- Gateway de pagamento ou estorno financeiro real.
- Regras de antecedência ou capacidade de pessoas por área.
- Autenticação com senhas ou OAuth (o apartamento enviado no `POST /sessoes` representa o morador autenticado).
