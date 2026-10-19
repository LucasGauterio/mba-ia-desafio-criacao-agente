---
name: design-docs-validate
description: Audita a consistência da documentação em docs/, a integridade dos links relativos e a conformidade com as regras do desafio.
---

# design-docs-validate: Validação Documental e Integridade

## Objetivo
Verificar se todos os arquivos em `docs/` (`PRD.md`, `RFC.md`, `FDD.md`, `TRACKER.md`, `adrs/`, `project-plan.md`, `phases/`) estão consistentes, sem links quebrados e fiéis ao código real.

## Checklist de Validação
1. **Links de Arquivos e Linhas**: Todos os links no formato `src/aurora/arquivo.py#Lnn` apontam para arquivos e linhas existentes.
2. **Imutabilidade de `dados/`**: Conferir que nenhum arquivo em `dados/` foi modificado em relação ao repositório base.
3. **Ausência de Segredos**: Garantir que `.env` não está no Git e que `.env.example` não contém chaves preenchidas.
4. **Presença das 5 Garantias**: Confirmar que as 5 Garantias estão documentadas no `README.md`, `PRD.md`, `RFC.md` e `TRACKER.md`.
5. **Critérios de Aceite**: Verificar que todos os critérios de aceite do `DESAFIO.md` possuem status auditado.

## Saída
Relatório de validação com status `clean` ou lista de inconformidades para correção.
