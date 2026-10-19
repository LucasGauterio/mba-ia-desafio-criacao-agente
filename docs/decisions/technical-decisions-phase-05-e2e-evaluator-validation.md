# Decisões Técnicas — Fase 05: Suíte E2E & Fluxo do Avaliador

## Testar a lógica de negócio determinística (`tools.py`) diretamente com `tool_context` mockado
- **Alternativas consideradas**: testar exclusivamente via `POST /mensagens` contra um LLM real.
- **Justificativa**: alinhado ao princípio arquitetural do projeto — "o modelo decide o caminho, o código decide o que é permitido" (`CONTEXT.md`). As garantias críticas de negócio (G1, G2, G5, RN01-RN05) são implementadas em Python puro e podem/devem ser verificadas deterministicamente, sem depender de uma chamada de rede não-determinística a um LLM.

## Limitação conhecida (antes desta revisão)
Essa estratégia nunca verificava se o LLM de fato roteia para a tool certa numa conversa real, e isso foi usado para justificar deixar os Passos 11, 12 e 13 do avaliador **sem nenhum teste equivalente**, automatizado ou não — um gap real, não uma limitação arquitetural legítima, já que Passos 12 e 13 não dependem de comportamento do LLM.

## Ação corretiva aplicada (ver `validation.md` desta fase)
- **Passo 13** (resiliência a reinício / Garantia 3): não depende de LLM — passa a ter teste automatizado que recria `Runner`/`DatabaseSessionService` sobre o mesmo arquivo de banco.
- **Passo 12** (regulamento seletivo): a parte determinística (eventos restritos ao capítulo correto) passa a ter teste automatizado via mock da fronteira do `Runner` (sem precisar de LLM real); a decisão do LLM em *escolher* consultar o capítulo certo continua sendo uma limitação real, verificável apenas manualmente via `TEST_PLAN.md` com `GEMINI_API_KEY`/`GOOGLE_API_KEY` configurada.
- **Passo 11** (visitante): passa a ser referenciado explicitamente na narrativa cumulativa de `test_evaluator_flow.py`, em vez de ficar isolado em `test_tools.py` sem relação nomeada com o passo do avaliador.
