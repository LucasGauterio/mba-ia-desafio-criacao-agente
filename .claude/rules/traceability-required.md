# Regra: Rastreabilidade Obrigatória (traceability-required)

## Diretivas Obrigatórias
1. **Mapeamento de Requisitos para Código e Testes**:
   - Todo requisito de negócio (`RN01` a `RN05`), cada uma das **5 Garantias** e cada passo do **Fluxo do Avaliador (Passos 1 a 15)** devem possuir links de rastreabilidade documentados em `docs/TRACKER.md`.
2. **Formato de Links de Linha**:
   - Sempre que referenciar funções, tabelas ou testes, utilize o formato de link com linha ou range: `src/aurora/tools.py#L45-L70` ou `tests/test_tools.py#L30`.
