---
name: plan-context
description: Consolida o contexto técnico de uma fase (dependências, restrições, resumo técnico) em docs/phases/phase-NN-{slug}/CONTEXT.md a partir das decisões já registradas pela skill research.
---

# plan-context: Consolidação de Contexto de Fase

## Objetivo
Escrever um resumo técnico curto e objetivo da fase: o que ela resolve, por que, e quais restrições de negócio (RN01-RN05, as 5 Garantias) se aplicam. Consome `docs/decisions/technical-decisions-phase-NN-{slug}.md` (skill `research`) como insumo — não repete o conteúdo da ADR ou do PRD, apenas referencia.

## Arquivo Gerado
`docs/phases/phase-NN-{slug}/CONTEXT.md`.

## Pré-requisito
`docs/decisions/technical-decisions-phase-NN-{slug}.md` deve existir (rodar `research` primeiro se não existir).
