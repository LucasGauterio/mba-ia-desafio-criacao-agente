# Fase 05: Suíte E2E & Fluxo do Avaliador

## Objetivo
Implementar e executar o teste de ponta a ponta que reproduz com exatidão os 15 passos sequenciais do fluxo do avaliador contra a API em execução, auditando todas as respostas, eventos e garantias.

Bibliotecas decididas nesta fase: ver [`library-refs.md`](library-refs.md).

## Step Implementations (SIs)
1. **SI-05-01**: Implementar [`tests/test_evaluator_flow.py`](../../../tests/test_evaluator_flow.py) cobrindo os passos 1 a 15 de forma determinística e encadeada.
2. **SI-05-02**: Validar concorrência simultânea (Passo 14) com requisições assíncronas paralelas via `asyncio.gather` e `httpx.AsyncClient`.
3. **SI-05-03**: Validar resiliência a reinício (Passo 13) recriando a instância do `Runner`/`API` sobre o mesmo arquivo de banco de dados.
4. **SI-05-04**: Atualizar a matriz de rastreabilidade em [`docs/TRACKER.md`](../../TRACKER.md).

## Entregáveis e Critérios de Conclusão
- [x] Passos 1, 2, 5, 6, 7, 8, 10, 14 cobertos por `tests/test_evaluator_flow.py` (chamando as tools determinísticas diretamente com `tool_context` mockado).
- [x] Passo 9 (404/409) coberto por `tests/test_api_contract.py#L39-L65`.
- [x] Passo 3 e 4 (isolamento de sessão e tentativa de cancelamento alheio) cobertos por `tests/test_evaluator_flow.py#L34-L46`.
- [x] Passo 14 (disputa concorrente) validado com `asyncio.gather` e verificação de exatamente 1 reserva gravada — [tests/test_evaluator_flow.py#L106-L135](../../../tests/test_evaluator_flow.py#L106-L135).
- [x] **Passo 11**: integrado à narrativa cumulativa do avaliador — [tests/test_evaluator_flow.py#L34-L58](../../../tests/test_evaluator_flow.py#L34-L58) (`test_passo_11_autorizacao_de_visitante_exige_confirmacao_do_sistema`).
- [x] **Passo 12**: consulta seletiva do regulamento validada dentro do fluxo (resposta + ausência de outros capítulos nos eventos) — [tests/test_api_integration.py](../../../tests/test_api_integration.py) (`test_passo_12_consulta_seletiva_do_regulamento_sem_vazar_outros_capitulos`).
- [x] **Passo 13**: resiliência a reinício (Garantia 3) validada recriando o `Runner`/`DatabaseSessionService` sobre o mesmo banco — [tests/test_api_integration.py](../../../tests/test_api_integration.py) (`test_passo_13_resiliencia_a_reinicio_sem_reset`).
- **Limitação aceita**: os Passos 12/13 e os caminhos de sucesso de `POST /mensagens`/`POST /confirmacoes` são validados mockando a fronteira do `Runner` (objetos `google.adk.events.Event` reais, sem chamar o LLM) — prova que a camada determinística (FastAPI + extração de eventos) funciona corretamente dado um evento do ADK no formato esperado, não que o LLM de fato produzirá esse evento. Ver [`docs/decisions/technical-decisions-phase-05-e2e-evaluator-validation.md`](../../decisions/technical-decisions-phase-05-e2e-evaluator-validation.md).
- [x] Passo 15 (auditoria final) é um critério manual de repositório (dependências fixadas, sem chaves versionadas), não requer teste automatizado.
