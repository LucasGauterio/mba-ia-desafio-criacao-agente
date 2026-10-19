# Regra: Restrição de Escopo do Workspace (restricao_escopo)

## Diretivas Obrigatórias
1. **Fronteira Estrita do Repositório**:
   - Todas as operações de leitura, edição, criação e execução de comandos DEVEM ser restritas ao diretório do projeto `mba-ia-desafio-criacao-agente`.
   - É expressamente proibido alterar arquivos fora do repositório, em diretórios temporários externos ou pastas de sistema.
2. **Imutabilidade de `dados/`**:
   - Os arquivos em `dados/` (`apartamentos.json`, `areas.json`, `regulamento.md`, `reservas.json`, `visitantes.json`) são imutáveis e representam o estado inicial oficial do condomínio.
   - Qualquer mutação de dados em tempo de execução deve ocorrer no banco de dados local (`storage/aurora.db`), nunca nos arquivos de `dados/`.
3. **Escopo Arquitetural Focado Exclusivamente em API e Agentes**:
   - O projeto NÃO possui frontend gráfico, React, Next.js, Node.js ou NestJS. Qualquer menção ou dependência de interfaces visuais está expressamente fora de escopo.
