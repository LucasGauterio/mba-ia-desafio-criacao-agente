# Regra: Princípio DRY e Consistência Documental (no-cross-document-duplication)

## Diretivas Obrigatórias
1. **Fonte Única da Verdade**:
   - `CONTEXT.md` centraliza o estado geral da aplicação e regras.
   - `AGENTS.md` e `CLAUDE.md` são ponteiros leves com links diretos para `CONTEXT.md`.
2. **Evitar Duplicação Desnecessária**:
   - Decisões de design são detalhadas em `docs/adrs/ADR-*.md` e apenas referenciadas no `PRD.md` e `RFC.md`.
   - Especificações funcionais e contratos residem no `FDD.md` e no `DESAFIO.md`.
   - A matriz de rastreabilidade em `docs/TRACKER.md` referencia números de linhas e arquivos, sem reescrever o texto completo dos requisitos.
