# ADR-005: Recuperação Seletiva de Regulamento por Capítulo

## Status
Aceito (Accepted)

## Contexto
O arquivo `dados/regulamento.md` contém quase 500 linhas e 14 capítulos abrangendo regras de animais, silêncio, mudanças, obras, piscina e áreas comuns. A Garantia 4 proíbe que o agente principal receba o regulamento em suas instruções e exige que nenhum evento gravado na sessão contenha trechos de capítulos que tratem de outros assuntos não relacionados à dúvida do morador.

## Decisão
1. **Instruções Limpas no Root**: `recepcao_aurora` não possui nenhuma linha do regulamento em seu prompt.
2. **Índice Resumido no Especialista**: O `agente_regulamento` recebe apenas a lista com os títulos dos 14 capítulos (I a XIV).
3. **Tool Granular de Leitura**: A tool `consultar_capitulo_regulamento(capitulo: int)` faz o parse em tempo de execução de `dados/regulamento.md` e devolve estritamente o capítulo solicitado (ex: ao perguntar da piscina aos domingos, devolve apenas o Capítulo IV - Piscina, Artigos 21 a 28).

## Consequências
- **Positivas**: Redução substancial de tokens; eventos da sessão permanecem limpos e sem poluição cruzada entre capítulos.
- **Negativas**: O LLM especialista precisa fazer o roteamento correto para o número do capítulo antes de invocar a tool.
