---
name: design-docs-fdd
description: Gera ou atualiza o Functional Design Document (FDD) em docs/FDD.md, contendo diagramas Mermaid C4, fluxos de sequência e modelo de dados.
---

# design-docs-fdd: Especificação de Design Funcional

## Objetivo
Produzir `docs/FDD.md` contendo especificações detalhadas das entidades, diagramas arquiteturais e sequenciais em Mermaid, fluxos de execução das tools e contratos de endpoints.

## Conteúdo Obrigatório
1. **Diagrama de Arquitetura C4 / Fluxo Geral (Mermaid)**:
   - Cliente HTTP / Avaliador -> FastAPI -> Runner/App ADK -> Root Agent -> Especialistas -> FunctionTools -> SQLite & `dados/`.
2. **Diagrama Sequencial da Garantia 1 (Confirmação)**:
   - Fluxo completo de requisição, pausa com `adk_request_confirmation`, resposta pela rota `/confirmacoes` e retomada da tool.
3. **Diagrama Sequencial da Garantia 5 (Concorrência)**:
   - Duas requisições paralelas com `&`, lock `BEGIN IMMEDIATE`, inserção vitoriosa e interceptação de `sqlite3.IntegrityError` com `200 OK`.
4. **Modelo de Dados (Diagrama ER Mermaid)**:
   - Tabelas: `apartamentos`, `areas`, `reservas`, `codigos_reserva_usados`, `visitantes` e tabelas do ADK (`sessions`, `events`).
5. **Especificação de cada Tool**:
   - Assinatura, entradas, saídas esperadas e comportamento de exceção.

## Saída
Arquivo `docs/FDD.md`.
