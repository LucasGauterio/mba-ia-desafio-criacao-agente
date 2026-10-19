---
name: design-docs-prd
description: Gera ou atualiza o Product Requirements Document (PRD) para a API e os Agentes de IA do Residencial Aurora em docs/PRD.md.
---

# design-docs-prd: PRD do Residencial Aurora

## Objetivo
Gerar ou atualizar `docs/PRD.md` com foco em regras de negócio, requisitos funcionais, as 5 garantias inegociáveis, endpoints da API e critérios de aceitação.

## Entradas
- `DESAFIO.md`: Enunciado oficial e critérios de aceite.
- `CONTEXT.md`: Fonte única da verdade.
- `.agents/rules/*`: Regras de negócio, segurança e confirmações.

## Seções Obrigatórias do PRD
1. **Visão Geral e Contexto**: Problema do condomínio, objetivos do assistente e personas (morador, síndica, avaliador).
2. **Regras de Negócio Centrais**: RN01 a RN05 detalhadas.
3. **Requisitos Funcionais (RF)**:
   - RF01: Criação e isolamento de sessão por apartamento.
   - RF02: Consulta e criação de reservas com cobrança/taxa zero.
   - RF03: Cancelamento de reservas próprias.
   - RF04: Autorização de visitantes com liberação de acesso físico.
   - RF05: Consulta seletiva ao regulamento interno.
4. **As 5 Garantias Críticas de Negócio**: Detalhadas com critérios objetivos de validação.
5. **Contrato da API HTTP**: Especificação dos payloads, status codes (201, 200, 404, 409).
6. **Fora de Escopo**: Interfaces visuais, pagamentos reais, autenticação externa.
7. **Critérios de Aceitação e Métricas de Qualidade**: 100% de conformidade com o fluxo do avaliador.

## Saída
Arquivo `docs/PRD.md`.
