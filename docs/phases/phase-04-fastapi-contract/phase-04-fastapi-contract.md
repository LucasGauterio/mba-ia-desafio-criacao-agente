# Fase 04: API FastAPI & Contrato HTTP

## Objetivo
Implementar a API HTTP com FastAPI respondendo em `http://localhost:8000`, cobrindo todos os endpoints, códigos de status e formatação do contrato do `DESAFIO.md`.

Bibliotecas decididas nesta fase: ver [`library-refs.md`](library-refs.md).

## Step Implementations (SIs)
1. **SI-04-01**: Definir modelos Pydantic de entrada e saída em [`src/aurora/api.py`](../../../src/aurora/api.py).
2. **SI-04-02**: Implementar `POST /sessoes` vinculando o apartamento no estado inicial da sessão e retornando `201 Created`.
3. **SI-04-03**: Implementar `POST /sessoes/{id}/mensagens` serializando execuções e extraindo `confirmacoes_pendentes` a partir dos eventos do ADK.
4. **SI-04-04**: Implementar `POST /sessoes/{id}/confirmacoes` com validação de status `409 Conflict` (se o ID não for pendente na sessão) e retomada do `Runner`.
5. **SI-04-05**: Implementar `GET /sessoes/{id}/eventos` devolvendo a lista de eventos completa e ordenada.
6. **SI-04-06**: Implementar `GET /apartamentos/{num}/reservas` e `GET /apartamentos/{num}/visitantes` consultando diretamente o banco SQLite.
7. **SI-04-07**: Criar testes automatizados de contrato em [`tests/test_api_contract.py`](../../../tests/test_api_contract.py).

## Entregáveis e Critérios de Conclusão
- [x] `POST /sessoes` retorna `201` com `session_id` — [tests/test_api_contract.py#L29-L35](../../../tests/test_api_contract.py#L29-L35).
- [x] Rotas com `session_id` inexistente retornam `404` (`/mensagens`, `/eventos`, `/confirmacoes`) — [tests/test_api_contract.py#L39-L45](../../../tests/test_api_contract.py#L39-L45).
- [x] Confirmação com ID não pendente retorna `409 Conflict` — [tests/test_api_contract.py#L55-L65](../../../tests/test_api_contract.py#L55-L65).
- [x] `GET /apartamentos/{num}/reservas` e `/visitantes` leem direto do SQLite — [tests/test_api_contract.py#L8-L25](../../../tests/test_api_contract.py#L8-L25).
- [x] Caminho de sucesso de `POST /sessoes/{id}/mensagens` (SI-04-03), `POST /sessoes/{id}/confirmacoes` com `confirmado: true` (SI-04-04) e `GET /sessoes/{id}/eventos` (SI-04-05) cobertos — [tests/test_api_integration.py](../../../tests/test_api_integration.py).
