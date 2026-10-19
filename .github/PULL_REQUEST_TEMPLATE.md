# Pull Request: Assistente Virtual do Residencial Aurora

## Descrição das Alterações
<!-- Descreva de forma concisa as mudanças introduzidas por este PR (foco em API ou Agentes de IA). -->

## Garantias e Regras de Negócio Verificadas
- [ ] **Garantia 1 (Confirmação):** Ações com taxa > 0 ou liberação de visitantes exigem confirmação via sistema; cancelamentos e taxa zero executam diretamente. Rota de confirmações retorna 409 para IDs inválidos.
- [ ] **Garantia 2 (Isolamento de Sessão):** Apartamento extraído exclusivamente do estado da sessão (`ToolContext.state["apartamento"]`). Nenhuma tool aceita parâmetro do LLM sem validação. Sem vazamento de dados de terceiros.
- [ ] **Garantia 3 (Persistência):** Sessões, eventos e mutações sobrevivem a reinício da API no SQLite. Códigos de reserva nunca se repetem.
- [ ] **Garantia 4 (Regulamento Seletivo):** O agente principal não contém o regulamento no prompt. O regulamento é lido de forma granular por capítulo apenas pelo especialista.
- [ ] **Garantia 5 (Concorrência Atômica):** Exclusividade garantida no instante do `INSERT` com `UNIQUE(area, data)` e `BEGIN IMMEDIATE`. Conflitos simultâneos retornam 200 com mensagem tratada.

## Checklist de Qualidade
- [ ] `uv sync` roda sem erros com versões fixadas.
- [ ] Testes automatizados executados (`pytest`) com 100% de sucesso.
- [ ] Rastreabilidade atualizada em `docs/TRACKER.md`.
- [ ] Sem chaves ou credenciais versionadas (Zero-Trust).
