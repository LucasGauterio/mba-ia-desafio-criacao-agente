---
name: design-docs-adr
description: Gera ou atualiza os registros de decisões arquiteturais (ADRs) em docs/adrs/ADR-*.md.
---

# design-docs-adr: Architecture Decision Records (ADRs)

## Objetivo
Gerenciar os registros formais de decisões arquiteturais no diretório `docs/adrs/`.

## Estrutura Padrão de um ADR
- **Título**: `ADR-NNN: <Decisão Curta>`
- **Status**: `Aceito` (Accepted)
- **Contexto**: A tensão técnica, requisito ou garantia que motivou a decisão.
- **Decisão**: A solução técnica adotada, citando bibliotecas, padrões e arquivos.
- **Consequências**:
  - Pontos positivos (benefícios, garantias atendidas).
  - Pontos negativos / custos (complexidade adicional, dependências).
- **Conformidade com as Regras do Desafio**: Validação contra o `DESAFIO.md`.

## ADRs Centrais do Projeto
- `ADR-001-multiagent-coordinator-specialists.md`: Topologia Coordenador + Especialistas via Sub-Agents no Google ADK.
- `ADR-002-sqlite-concurrency-unique-constraint.md`: Exclusividade atômica com `UNIQUE(area, data)` e `BEGIN IMMEDIATE`.
- `ADR-003-session-state-isolation-anti-injection.md`: Isolamento de apartamento via `ToolContext.state` sem parâmetro no LLM.
- `ADR-004-tool-confirmation-lifecycle.md`: Ciclo de vida de confirmação via `request_confirmation` e validação 409 na API.
- `ADR-005-selective-regulation-retrieval.md`: Consulta seletiva de regulamento por capítulo sem injeção no prompt inicial.

## Saída
Arquivos em `docs/adrs/`.
