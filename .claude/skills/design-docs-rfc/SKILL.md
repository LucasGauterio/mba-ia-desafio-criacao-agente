---
name: design-docs-rfc
description: Gera ou atualiza a proposta técnica e de arquitetura (RFC) em docs/RFC.md, cobrindo Google ADK v2, FastAPI, SQLite e controle de concorrência.
---

# design-docs-rfc: Proposta Técnica da Solução

## Objetivo
Documentar as decisões técnicas, trade-offs de engenharia, escolhas de bibliotecas e padrões de arquitetura para a API e os Agentes de IA em `docs/RFC.md`.

## Tópicos a Cobrir
1. **Contexto e Motivação**: Por que uma abordagem com agentes LLM exige salvaguardas determinísticas em código (*"O modelo decide o caminho, o código decide o que é permitido"*).
2. **Proposta de Arquitetura**:
   - Google ADK v2.2.0: Topologia Coordenador + Especialistas via Sub-Agents.
   - Padrão de execução assíncrono com `Runner` e `App` com `ResumabilityConfig(is_resumable=True)`.
   - Persistência com `DatabaseSessionService` em SQLite com WAL mode.
3. **Mecanismos das 5 Garantias**:
   - G1: Tool confirmation nativo e rota HTTP com validação 409.
   - G2: Injeção de apartamento via `tool_context.state` sem parâmetro no LLM.
   - G3: Persistência integral de eventos e dados em SQLite.
   - G4: Consulta seletiva de regulamento por capítulo sem injeção no prompt inicial.
   - G5: Restrição `UNIQUE(area, data)` e transações imediatas no banco.
4. **Trade-offs Avaliados**:
   - Sub-Agents vs AgentTools independentes.
   - SQLite WAL vs PostgreSQL/MySQL em container.
   - Polling vs Eventos em sessão única.
5. **Impacto em Segurança e Desempenho**: Redução de consumo de tokens, prevenção de prompt injection e contenção de concorrência.

## Saída
Arquivo `docs/RFC.md`.
