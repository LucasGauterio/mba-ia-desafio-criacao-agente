# Referência de Bibliotecas da Fase 06

| Ferramenta | Papel no SI | ADR/Decisão Relacionada |
| :--- | :--- | :--- |
| `bash` (script `scripts/run_test_plan.sh`) | SI-06-01 — orquestra todo o ciclo de vida da API real (reset, start, requisições, restart no CT-13, concorrência real no CT-14) | [technical-decisions-phase-06](../../decisions/technical-decisions-phase-06-test-plan-execution.md) |
| `curl` | SI-06-01 — cliente HTTP para todas as requisições do roteiro | — |
| `uv` / `.venv` (Python do projeto) | SI-06-01 — resolução do interpretador (`uv run python -c "...sys.executable"` com fallback para `.venv/`) e extração de campos JSON via `json.load` inline | [technical-decisions-phase-06](../../decisions/technical-decisions-phase-06-test-plan-execution.md) |
| `netstat` / `taskkill` (Windows) | SI-06-01 — identificação e encerramento do processo real da API pelo número da porta, para o reinício do CT-13 | [technical-decisions-phase-06](../../decisions/technical-decisions-phase-06-test-plan-execution.md) |

## Observações
- Nenhuma dependência nova foi adicionada a `pyproject.toml` nesta fase — o script usa apenas o interpretador Python já provisionado pelo `uv sync` e ferramentas de linha de comando (`curl`, `netstat`, `taskkill`) já disponíveis no ambiente.
