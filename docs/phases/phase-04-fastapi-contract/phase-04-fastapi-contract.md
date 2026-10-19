# Fase 04: API FastAPI & Contrato HTTP

## Objetivo
Implementar a API HTTP com FastAPI respondendo em `http://localhost:8000`, cobrindo todos os endpoints, códigos de status e formatação do contrato do `DESAFIO.md`.

## Step Implementations (SIs)
1. **SI-04-01**: Definir modelos Pydantic de entrada e saída em [`src/aurora/api.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/api.py).
2. **SI-04-02**: Implementar `POST /sessoes` vinculando o apartamento no estado inicial da sessão e retornando `201 Created`.
3. **SI-04-03**: Implementar `POST /sessoes/{id}/mensagens` serializando execuções e extraindo `confirmacoes_pendentes` a partir dos eventos do ADK.
4. **SI-04-04**: Implementar `POST /sessoes/{id}/confirmacoes` com validação de status `409 Conflict` (se o ID não for pendente na sessão) e retomada do `Runner`.
5. **SI-04-05**: Implementar `GET /sessoes/{id}/eventos` devolvendo a lista de eventos completa e ordenada.
6. **SI-04-06**: Implementar `GET /apartamentos/{num}/reservas` e `GET /apartamentos/{num}/visitantes` consultando diretamente o banco SQLite.
7. **SI-04-07**: Criar testes automatizados de contrato em [`tests/test_api_contract.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/tests/test_api_contract.py).
