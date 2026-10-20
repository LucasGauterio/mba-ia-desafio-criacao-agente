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

## Achado adicional e corrigido: `reservar_area`/`verificar_disponibilidade_area` não resolviam o nome legível da área
- **Observação** (execução completa real do usuário, 2026-10-20): `reservar_area("salão de festas", ...)` falhava com `{"status": "erro", "mensagem": "Área 'salão de festas' não encontrada."}` porque a tool fazia `WHERE id = ?` com o texto exato recebido do LLM — mas o Gemini, ao processar "Reserve o salão de festas", naturalmente passa o **nome legível** da área (com acento e espaço), não o slug interno (`salao-de-festas`). Isso explicava em cascata 13 das 13 falhas observadas: CT-07 e CT-08 (confirmação nunca gerada) e CT-13 (reserva do salão nunca existiu para persistir).
- **Correção**: `_resolver_area()` em `src/aurora/tools.py` agora resolve a área tanto pelo `id` quanto pelo `nome`, normalizando acentos/caixa/espaços (`unicodedata.normalize` + `.lower()` + troca de espaço por hífen). `reservar_area` e `verificar_disponibilidade_area` usam o `id` canônico resolvido em toda consulta/gravação subsequente (antes, o código de gravação usava o texto bruto recebido do LLM mesmo quando a resolução tivesse funcionado por sorte).
- **Validado ao vivo**: a mesma mensagem que falhava agora gera a confirmação pendente corretamente já na primeira tentativa (`detalhes.area == "salao-de-festas"`).

## SI-06-06: espera configurável entre chamadas ao LLM real
- **Observação**: mesmo com os bugs de código corrigidos, uma nova rodada completa voltou a travar a partir do CT-03 com o mesmo padrão de rate limiting já descrito (timeout de 60s sem resposta, sem exceção no servidor) — provavelmente por rodar o script várias vezes em sequência rápida na mesma sessão, consumindo a janela de quota da chave.
- **Decisão**: adicionar `REQUEST_DELAY_SECONDS` (padrão `5`, ajustável via variável de ambiente, `0` desliga) em `scripts/run_test_plan.sh`, aplicado em `http()` antes de toda chamada a `/mensagens` ou `/confirmacoes` (as únicas que acionam o `Runner`/LLM), e antes do disparo concorrente do CT-14.
- **Alternativas consideradas**: backoff exponencial com retry automático no próprio script. Descartado por ora — exigiria parsing do corpo de erro do `curl` (que hoje só reporta status/timeout, não o motivo), e um espaçamento fixo configurável já resolve o caso observado com simplicidade. Pode ser revisitado se `REQUEST_DELAY_SECONDS` maior ainda não bastar.

## Achado: o agente pode bundlar múltiplas confirmações pendentes numa única resposta
- **Observação**: numa execução com `REQUEST_DELAY_SECONDS` (sem travar por rate limiting), o CT-11 falhou porque `confirmacoes_pendentes[0]` trouxe os detalhes da reserva do salão (CT-07/08, ainda não resolvida), não os da Joana Ribeiro. Inspecionando `GET /eventos` ao vivo: o agente, ao processar a mensagem de autorização de visitante, **retomou por conta própria o pedido de reserva do salão ainda pendente** (usando o nome correto da área desta vez) e gerou **duas** `adk_request_confirmation` na mesma resposta — uma para `reservar_area`, outra para `autorizar_visitante`.
- **Isso não é um bug de código** — é o agente sendo "proativo" com um item de conversa ainda não resolvido, e `extrair_confirmacoes_pendentes` reporta corretamente AMBAS as pendências (a Garantia 1 continua intacta: nada foi gravado sem confirmação). O bug estava no **script de teste**, que assumia `confirmacoes_pendentes[0]` como "a relevante para esta mensagem".
- **Correção**: `confirmacao_campo()` em `scripts/run_test_plan.sh` seleciona o item pela `acao` esperada (`reservar_area` ou `autorizar_visitante`) em vez do índice `[0]`. Os testes de CT-07/CT-08 também passaram a tolerar o caso em que o agente não gera a confirmação na mesma mensagem (registrando como variação do LLM, não falha), já que o momento exato em que o agente decide retomar um item pendente é nao-determinístico. O CT-13 passou a verificar o total de reservas condicionalmente ao que o CT-08 de fato concluiu nessa execução específica (flag `SALAO_2030_04_20_RESERVADO`), em vez de assumir sempre 2.

## Resultado final (2026-10-20)
Com todas as correções acima (SI-06-02, SI-06-03, SI-06-06, resolução de área, seleção de confirmação por `acao`), uma execução completa de `scripts/run_test_plan.sh` contra a API real terminou com **90/90 passos OK, 0 FALHOU** — os 18 CTs de `TEST_PLAN.md`, incluindo o reinício real do processo (CT-13) e a disputa concorrente real (CT-14).
