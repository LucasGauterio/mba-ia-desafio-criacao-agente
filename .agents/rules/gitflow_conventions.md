# Regra: Convenções GitFlow e Commits (gitflow_conventions)

## Diretivas Obrigatórias
1. **Padrão Conventional Commits**:
   - `feat(escopo): descrição concisa` para novas funcionalidades.
   - `fix(escopo): correção de bug ou falha de regra`.
   - `docs(escopo): atualizações de documentação e ADRs`.
   - `test(escopo): adição ou ajuste de suíte de testes`.
   - `refactor(escopo): refatoração sem alteração de comportamento`.
   - `chore(escopo): ajustes de configuração, dependências ou scripts`.
2. **Estratégia de Branches**:
   - `main`: Branch de entrega final estável e testada.
   - `dev` / `feature/*`: Branches de trabalho e fases do plano de implementação.
