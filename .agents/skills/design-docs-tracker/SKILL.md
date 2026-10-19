---
name: design-docs-tracker
description: Mantém a matriz de rastreabilidade (Traceability Matrix) em docs/TRACKER.md mapeando regras, garantias e passos do avaliador para o código e testes.
---

# design-docs-tracker: Matriz de Rastreabilidade

## Objetivo
Manter `docs/TRACKER.md` como a fonte de auditoria cruzada entre as especificações do `DESAFIO.md`, o código de implementação em `src/aurora/` e a suíte de testes em `tests/`.

## Estrutura da Matriz
| ID Requisito | Descrição Curta | Arquivo de Implementação | Linha/Símbolo | Teste Automatizado | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **RN01** | Exclusividade de Reserva por Área e Data | `src/aurora/database.py`<br>`src/aurora/tools.py` | `UNIQUE(area, data)`<br>`reservar_area` | `tests/test_database.py`<br>`tests/test_tools.py` | ✅ Implementado |
| **RN02** | Cobrança se Taxa > 0 / Isenção se Taxa == 0 | `src/aurora/tools.py` | `reservar_area` | `tests/test_tools.py` | ✅ Implementado |
| **RN03** | Autorização de Visitante com Confirmação | `src/aurora/tools.py` | `autorizar_visitante` | `tests/test_tools.py` | ✅ Implementado |
| **RN04** | Cancelamento de Reserva Própria sem Confirmação | `src/aurora/tools.py` | `cancelar_minha_reserva` | `tests/test_tools.py` | ✅ Implementado |
| **RN05** | Unicidade Perpétua de Códigos de Reserva | `src/aurora/database.py`<br>`src/aurora/tools.py` | `codigos_reserva_usados` | `tests/test_database.py` | ✅ Implementado |
| **G1** | Cobrança ou Acesso Só com Confirmação | `src/aurora/tools.py`<br>`src/aurora/api.py` | `request_confirmation`<br>`POST /confirmacoes` | `tests/test_tools.py`<br>`tests/test_api_contract.py` | ✅ Implementado |
| **G2** | Cada Sessão Pertence a um Apartamento | `src/aurora/api.py`<br>`src/aurora/tools.py` | `POST /sessoes`<br>`tool_context.state` | `tests/test_tools.py`<br>`tests/test_evaluator_flow.py` | ✅ Implementado |
| **G3** | Nada se Perde no Reinício | `src/aurora/agents.py`<br>`src/aurora/database.py` | `DatabaseSessionService`<br>`aurora.db` | `tests/test_evaluator_flow.py` | ✅ Implementado |
| **G4** | Regulamento Consultado, Não Carregado | `src/aurora/agents.py`<br>`src/aurora/regulamento.py` | `agente_regulamento`<br>`consultar_capitulo` | `tests/test_tools.py`<br>`tests/test_evaluator_flow.py` | ✅ Implementado |
| **G5** | Dois Moradores, Uma Reserva (Concorrência) | `src/aurora/database.py`<br>`src/aurora/tools.py` | `BEGIN IMMEDIATE`<br>`IntegrityError` | `tests/test_database.py`<br>`tests/test_evaluator_flow.py` | ✅ Implementado |

## Saída
Arquivo `docs/TRACKER.md`.
