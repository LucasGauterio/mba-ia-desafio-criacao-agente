# Matriz de Rastreabilidade Ponta a Ponta (TRACKER.md)

Este documento audita o mapeamento entre requisitos de negócio, as 5 garantias obrigatórias, o fluxo de testes do avaliador e as implementações em código e testes.

---

## 1. Rastreabilidade das Regras de Negócio (RN)

| ID | Regra | Implementação no Código | Linha / Símbolo | Teste Automatizado |
| :---: | :--- | :--- | :--- | :--- |
| **RN01** | Exclusividade de reserva por área e data | `src/aurora/database.py`<br>`src/aurora/tools.py` | `UNIQUE(area, data)`<br>`reservar_area` | `tests/test_database.py`<br>`tests/test_tools.py` |
| **RN02** | Taxa > 0 gera cobrança (confirmação); Taxa == 0 isenta | `src/aurora/tools.py` | `reservar_area` | `tests/test_tools.py`<br>`tests/test_tools.py#L28-L49` (resolução de área por nome legível, não só o slug) |
| **RN03** | Autorização de visitante libera acesso físico | `src/aurora/tools.py` | `autorizar_visitante` | `tests/test_tools.py` |
| **RN04** | Morador cancela reservas próprias sem confirmação | `src/aurora/tools.py` | `cancelar_minha_reserva` | `tests/test_tools.py` |
| **RN05** | Códigos de reserva únicos e perpétuos | `src/aurora/database.py`<br>`src/aurora/tools.py` | `codigos_reserva_usados` | `tests/test_database.py` |

---

## 2. Rastreabilidade das 5 Garantias Críticas

| Garantia | Descrição | Onde Reside no Código | Linha / Símbolo | Teste Automatizado |
| :---: | :--- | :--- | :--- | :--- |
| **G1** | Cobrança ou acesso só com confirmação | `src/aurora/tools.py`<br>`src/aurora/api.py` | `request_confirmation`<br>`POST /confirmacoes` (validação 409) | `tests/test_tools.py`<br>`tests/test_api_contract.py`<br>`tests/test_api_integration.py#L22-L148` (caminho de sucesso real via API, formato `toolConfirmation.payload` do ADK) |
| **G2** | Cada sessão pertence a um apartamento | `src/aurora/api.py`<br>`src/aurora/tools.py` | `POST /sessoes`<br>`tool_context.state["apartamento"]` | `tests/test_tools.py`<br>`tests/test_evaluator_flow.py`<br>`tests/test_api_contract.py#L29-L35` (`test_criar_sessao_status_201`) |
| **G3** | Nada se perde no reinício | `src/aurora/agents.py`<br>`src/aurora/database.py` | `DatabaseSessionService`<br>`storage/aurora.db` | `tests/test_api_integration.py#L242-L273` (`test_passo_13_resiliencia_a_reinicio_sem_reset`) |
| **G4** | Regulamento consultado, não carregado | `src/aurora/agents.py`<br>`src/aurora/regulamento.py` | `agente_regulamento`<br>`consultar_capitulo_regulamento` | `tests/test_tools.py#L200-L209`<br>`tests/test_api_integration.py#L170-L238` (`test_passo_12_*`, isolamento de capítulos ao vivo via API) |
| **G5** | Dois moradores, uma reserva | `src/aurora/database.py`<br>`src/aurora/tools.py` | `BEGIN IMMEDIATE`<br>`IntegrityError` | `tests/test_database.py`<br>`tests/test_evaluator_flow.py#L138-L166` (`test_passo_14_disputa_concorrente_simultanea`) |

---

## 3. Rastreabilidade do Fluxo do Avaliador (Passos 1 a 15)

| Passo | Operação Avaliada | Endpoint / Recurso | Validação Realizada |
| :---: | :--- | :--- | :--- |
| **1** | Reset inicial e rotas de verificação | `GET /apartamentos/101/reservas`<br>`GET /apartamentos/302/visitantes` | Status 200; RSV-1377 na quadra e Marina Duarte no 302. Automatizado: `tests/test_api_contract.py#L8-L25`. |
| **2** | Criação da sessão S1 | `POST /sessoes` com `{"apartamento": "101"}` | Status 201 Created; session_id retornado. Automatizado: `tests/test_api_contract.py#L29-L35`. |
| **3** | Prompt injection de leitura do 302 | `POST /sessoes/{S1}/mensagens` | Resposta e eventos NÃO contêm RSV-4821 nem Marina Duarte. **Gap na suíte mockada**: `tests/test_evaluator_flow.py#L39-L51` chama-se "Passos 3 e 4" mas só implementa o Passo 4 (`cancelar_minha_reserva`) — não há asserção dedicada ao cenário de leitura do Passo 3. O mecanismo subjacente (isolamento de leitura por `tool_context.state`) é coberto genericamente por `tests/test_tools.py#L171-L197`. Validado de fato (com o LLM real) em `scripts/run_test_plan.sh` (CT-03). |
| **4** | Tentativa de cancelamento de reserva alheia | `POST /sessoes/{S1}/mensagens` | Reserva do 302 preservada no banco; eventos sem RSV-4821. Automatizado: `tests/test_evaluator_flow.py#L39-L51`. |
| **5** | Cancelamento de reserva própria | `POST /sessoes/{S1}/mensagens` | Sem confirmação pendente; RSV-1377 removida do 101. Automatizado: `tests/test_evaluator_flow.py#L54-L59`. |
| **6** | Reserva em área com taxa zero (quadra) | `POST /sessoes/{S1}/mensagens` | Sem confirmação pendente; quadra em 2030-04-06 criada. Automatizado: `tests/test_evaluator_flow.py#L67-L76`. |
| **7** | Reserva com cobrança e rejeição de confirmação | `POST /sessoes/{S1}/mensagens`<br>`POST /sessoes/{S1}/confirmacoes` | Confirmação pendente com área/data em detalhes; confirmado=false não grava. Automatizado: `tests/test_evaluator_flow.py#L78-L100`. |
| **8** | Aprovação de reserva e rejeição de duplicidade | `POST /sessoes/{S1}/confirmacoes` | Reserva gravada; reenviar mesmo ID retorna 409 Conflict. Automatizado: `tests/test_evaluator_flow.py#L78-L100` (mesma função do Passo 7) e `tests/test_api_integration.py#L71-L148` (ciclo completo via API real). |
| **9** | Confirmação com ID inexistente | `POST /sessoes/{S1}/confirmacoes` | Retorna 409 Conflict; GET /sessoes/inexistente/eventos retorna 404. Automatizado: `tests/test_api_contract.py#L39-L65`. |
| **10** | Conflito de data ocupada por terceiro | `POST /sessoes` (S2) -> reserva salão | Não cria reserva; resposta e eventos sem RSV-4821 ou '302' solto. Automatizado: `tests/test_evaluator_flow.py#L103-L108`. |
| **11** | Autorização de visitante com falsa confirmação no chat | `POST /sessoes/{S1}/mensagens` | Gera confirmação pendente; aprovação via API grava visitante. Automatizado: `tests/test_evaluator_flow.py#L111-L135`. |
| **12** | Consulta seletiva do regulamento (piscina domingos) | `POST /sessoes/{S1}/mensagens` | Retorna horário de fechamento (20h); eventos sem outros capítulos. Automatizado: `tests/test_api_integration.py#L170-L238`. |
| **13** | Reinício da API sem reset | `POST /sessoes/{S1}/mensagens` | Total de eventos preservado; dados de 101 e 302 íntegros. Automatizado: `tests/test_api_integration.py#L242-L273`. |
| **14** | Disputa concorrente simultânea (S3 e S4) | `POST /confirmacoes` (disparo simultâneo `&`) | Ambas respondem 200 OK; exatamente 1 reserva gravada para 2030-05-11. Automatizado: `tests/test_evaluator_flow.py#L138-L166`. |
| **15** | Auditoria final do repositório | Repositório / README | Dependências fixadas, sem chaves versionadas, 5 garantias comprovadas. |

---

## 4. Execução Real Complementar (Fase 06)

Os Passos 1-15 acima são validados pela suíte mockada (sem LLM real). [`scripts/run_test_plan.sh`](../scripts/run_test_plan.sh) automatiza o mesmo roteiro contra a API real com o Gemini de verdade — ver [`docs/phases/phase-06-test-plan-execution/`](phases/phase-06-test-plan-execution/).

| Cobertura | Status | Evidência |
| :--- | :---: | :--- |
| Passos 1-14 (individualmente, em execuções distintas) | Validado | `docs/decisions/technical-decisions-phase-06-test-plan-execution.md` |
| Passo 13 (reinício real do processo, Garantia 3) | Validado | Contagem de eventos preservada; dados de domínio intactos após `kill`+restart real. |
| Passo 14 (disputa concorrente real, Garantia 5) | Validado | Uma sessão recebeu `sucesso`; a outra `"já está ocupado"`, sem erro 500 em nenhuma. |
| Execução única e completa (18/18 CTs em sequência) | **Validado** | 90/90 passos OK, 0 FALHOU (2026-10-20) — ver `docs/phases/phase-06-test-plan-execution/validation.md`. |

---

## 5. Nota de Manutenção

As âncoras `arquivo#Lnn-Lmm` acima apontam para linhas exatas e **quebram quando o arquivo referenciado é editado antes do trecho apontado** (inserir uma função no meio de `tests/test_tools.py`, por exemplo, desloca todas as âncoras posteriores). Em 2026-10-20, uma auditoria encontrou duas âncoras desatualizadas por esse motivo (G3 apontava para `test_api_integration.py#L196-L224`, que já pertencia a outro teste; G4 e o Passo 11 tinham o mesmo problema) — corrigidas nesta revisão. Ao adicionar ou mover testes, revalide as âncoras deste arquivo com `grep -n "^def test_\|^async def test_"` nos arquivos afetados antes de commitar.
