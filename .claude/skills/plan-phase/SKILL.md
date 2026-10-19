---
name: plan-phase
description: Planeja e estrutura uma nova fase ou sub-funcionalidade de API e Agentes, gerando contexto e validação em docs/phases/.
---

# plan-phase: Planejamento de Fase de API e Agentes

## Objetivo
Estruturar o planejamento técnico de uma fase específica (ex: Fase 01, 02, etc.) em `docs/phases/phase-NN-{slug}/`.

## Arquivos Gerados por Fase
1. `CONTEXT.md`: Contexto consolidado da fase, objetivos, dependências e restrições.
2. `validation.md`: Checklist arquitetural e validação de consistência (`clean` ou `dirty`).
3. `phase-NN-{slug}.md`: Plano de implementação com Step Implementations (SIs) atômicos, links para os arquivos-alvo (`src/aurora/arquivo.py#Lnn`) e critérios de entrega.

## Fases Oficiais do Projeto
- **Fase 01**: `phase-01-core-setup` (Ambiente uv, Schema SQLite, Seeds e CLI de Reset)
- **Fase 02**: `phase-02-storage-concurrency` (Camada de dados, transações atômicas e FunctionTools)
- **Fase 03**: `phase-03-adk-agents-tools` (Topologia multiagente ADK, subagents, regulamento)
- **Fase 04**: `phase-04-fastapi-contract` (API FastAPI, contrato REST, streaming de eventos e confirmações)
- **Fase 05**: `phase-05-e2e-evaluator-validation` (Testes ponta a ponta e auditoria dos 15 passos do avaliador)
