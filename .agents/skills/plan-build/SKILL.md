---
name: plan-build
description: Gera ou atualiza o plano de implementação da fase (Step Implementations, critérios de entrega) em phase-NN-{slug}.md e a referência de bibliotecas em library-refs.md.
---

# plan-build: Construção do Plano de Implementação

## Objetivo
A partir do contexto consolidado (`CONTEXT.md`) e das decisões técnicas (`docs/decisions/`), detalhar os Step Implementations (SIs) atômicos da fase, com links para os arquivos-alvo (`src/aurora/arquivo.py#Lnn`) e os critérios de entrega verificáveis (link para teste ou comando).

## Arquivos Gerados
1. `docs/phases/phase-NN-{slug}/phase-NN-{slug}.md`: Objetivo, Step Implementations (SIs), Entregáveis e Critérios de Conclusão.
2. `docs/phases/phase-NN-{slug}/library-refs.md`: bibliotecas decididas nesta fase (nome, versão em `pyproject.toml`, papel no SI, ADR relacionada quando houver).
