# Decisões Técnicas — Fase 06: Execução Automatizada do TEST_PLAN.md

## Script bash de automação em vez de um novo arquivo pytest
- **Alternativas consideradas**: adicionar os 18 casos de teste (CT-01 a CT-18) como mais um arquivo em `tests/`, ao lado de `test_evaluator_flow.py`.
- **Justificativa**: `TEST_PLAN.md` é, por definição (ver `docs/decisions/technical-decisions-phase-05-e2e-evaluator-validation.md`), o roteiro **manual/E2E contra o LLM real** — o oposto do que a suíte `pytest` decidiu ser (determinística, sem rede, sem chave de API). Misturar os dois violaria essa decisão já tomada na Fase 05. Um script `scripts/run_test_plan.sh` dedicado mantém a fronteira clara: `uv run pytest` nunca depende de `GEMINI_API_KEY`; `scripts/run_test_plan.sh` sempre depende.

## `curl` + Python inline (via `json_field`) em vez de `jq`
- **Alternativas consideradas**: `jq` para extração de campos JSON.
- **Justificativa**: `jq` não é uma dependência garantida no ambiente do avaliador/desenvolvedor; o projeto já depende de Python (via `uv`/`.venv`), então usar `python -c "import json..."` como extrator evita introduzir uma nova dependência externa de sistema.

## Resolução do interpretador via `uv run python -c "...sys.executable"` com fallback para `.venv/`
- **Alternativas consideradas**: assumir `python`/`python3` no `PATH`.
- **Justificativa**: o projeto é gerenciado exclusivamente por `uv` (`python-uv-conventions`); resolver o interpretador do ambiente correto (e não um Python global do sistema) evita rodar contra dependências desatualizadas ou ausentes.

## Bug corrigido: `wait` sem argumentos trava o script no CT-14
- **Observação**: `ct14()` disparava os dois `curl` concorrentes com `&` e depois chamava `wait` sem argumentos. Como `start_api()` também inicia a API com `&` no mesmo processo do shell, `wait` (bare) esperava **todos** os jobs em background — incluindo o processo da própria API, que nunca termina — travando o script indefinidamente logo após "Disparando as duas aprovações simultaneamente...".
- **Correção**: capturar o PID de cada `curl` (`$!` imediatamente após cada `&`) e usar `wait "$pid_s3" "$pid_s4"`, esperando apenas os dois jobs relevantes.

## Reinício real do processo no CT-13 (kill + restart), sem simulação
- **Alternativas consideradas**: apenas recriar o objeto `Runner` em memória, sem matar o processo do SO.
- **Justificativa**: o Passo 13 do avaliador testa a Garantia 3 ("nada se perde no reinício") precisamente contra a hipótese de perda de estado em memória; simular o reinício sem matar o processo do SO não provaria nada sobre persistência real em disco. No Windows, a identificação do processo é feita por porta (`netstat` + `taskkill //PID ... //F`), não pelo PID do job do bash, que nem sempre corresponde ao processo nativo do Windows quando lançado via Git Bash.

## Achado resolvido: `500`/erro em `POST /mensagens` — causas raiz identificadas (não é um bug único)
Depois de corrigir o truncamento do log (SI-06-03) e reproduzir isoladamente, foram identificadas **duas causas distintas** para os erros vistos nas primeiras execuções, nenhuma delas um "estado corrompido em memória":

1. **Bug de código real e determinístico (corrigido)**: `extrair_confirmacoes_pendentes` em `src/aurora/api.py` lia `args["payload"]`, mas o formato real retornado pelo ADK para `adk_request_confirmation` é `args["toolConfirmation"]["payload"]` (confirmado inspecionando `GET /eventos` ao vivo). Isso fazia `acao`/`detalhes` virarem `"confirmar_acao"`/`{}` em toda confirmação pendente real — nunca pego pelos testes mockados da Fase 04/05 porque os mocks reproduziam a MESMA suposição errada de formato. Corrigido em `api.py` e em `tests/test_api_integration.py` (mocks agora usam o formato real).
2. **Rate limiting / quota da API do Gemini (restrição externa, não um bug)**: ao reexecutar o roteiro completo rapidamente em sequência, `POST /mensagens` começou a travar os 60s inteiros sem resposta a partir de certo ponto (CT-07 em diante), sem nenhuma exceção logada no servidor — padrão consistente com o cliente `google-genai` retriando silenciosamente um erro de limite de taxa/quota da chave configurada. Isso explica também o padrão observado na primeira execução (falhas até o reinício do CT-13 "curar" o problema): o reinício, ao consumir ~15-40s em paradas/esperas, dava tempo para a janela de limite de taxa resetar.
- **Status**: SI-06-02 e SI-06-03 **concluídos**. A execução 18/18 limpa (SI-06-04) depende de uma chave com quota suficiente para a sequência completa, ou de um intervalo de espera entre chamadas no script — ver pendência correspondente em `validation.md`.
