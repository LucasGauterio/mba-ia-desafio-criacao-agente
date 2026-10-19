---
name: plan-phase
description: Executa o pipeline completo de planejamento de uma fase (research → plan-context → plan-validate → plan-resolve → plan-build) em sequência para phase-NN.
---

# plan-phase: Pipeline Completo de Planejamento de Fase

## Objetivo
Atalho que executa, em sequência, as 5 etapas formais do pipeline de planejamento para uma fase específica (ex: Fase 01, 02, etc.), sem duplicar a lógica de cada etapa.

## Etapas (nesta ordem)
1. **`research`** → `docs/decisions/technical-decisions-phase-NN-{slug}.md`.
2. **`plan-context`** → `docs/phases/phase-NN-{slug}/CONTEXT.md`.
3. **`plan-validate`** → `docs/phases/phase-NN-{slug}/validation.md` (`clean` ou `dirty`).
4. **`plan-resolve`** → fecha as pendências de `validation.md` até `clean`, ou documenta a limitação aceita em `docs/decisions/`.
5. **`plan-build`** → `docs/phases/phase-NN-{slug}/phase-NN-{slug}.md` (Step Implementations + Entregáveis) e `library-refs.md`.

Depois de uma fase já implementada, `plan-phase` pode ser invocada novamente para reauditar (repete `plan-validate` → `plan-resolve` com o estado atual do código).

## Fases Oficiais do Projeto
- **Fase 01**: `phase-01-core-setup` (Ambiente uv, Schema SQLite, Seeds e CLI de Reset)
- **Fase 02**: `phase-02-storage-concurrency` (Camada de dados, transações atômicas e FunctionTools)
- **Fase 03**: `phase-03-adk-agents-tools` (Topologia multiagente ADK, subagents, regulamento)
- **Fase 04**: `phase-04-fastapi-contract` (API FastAPI, contrato REST, streaming de eventos e confirmações)
- **Fase 05**: `phase-05-e2e-evaluator-validation` (Testes ponta a ponta e auditoria dos 15 passos do avaliador)
