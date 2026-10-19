# Regra: Contratos de Endpoints FastAPI (fastapi-endpoint-contracts)

## Diretivas Obrigatórias
1. **Conformidade Estrita com o Contrato**:
   - `POST /sessoes`: Recebe `{"apartamento": "..."}` -> Retorna `201 Created` `{"session_id": "..."}`.
   - `POST /sessoes/{id}/mensagens`: Recebe `{"texto": "..."}` -> Retorna `200 OK` `{"resposta": "...", "confirmacoes_pendentes": [...]}` ou `404 Not Found`.
   - `POST /sessoes/{id}/confirmacoes`: Recebe `{"id": "...", "confirmado": bool}` -> Retorna `200 OK` com o mesmo formato de mensagens, `409 Conflict` se a confirmação não for pendente na sessão, ou `404 Not Found`.
   - `GET /sessoes/{id}/eventos`: Retorna `200 OK` com a lista cronológica de eventos com conteúdo completo, ou `404 Not Found`.
   - `GET /apartamentos/{num}/reservas`: Retorna `200 OK` lendo diretamente do banco (`[{"codigo": "...", "area": "...", "data": "AAAA-MM-DD"}]`).
   - `GET /apartamentos/{num}/visitantes`: Retorna `200 OK` lendo diretamente do banco (`[{"nome": "...", "data": "AAAA-MM-DD"}]`).
2. **Serialização e Robustez**:
   - As rotas devem utilizar Pydantic v2 para validação de entrada e saída.
   - Chamadas concorrentes na mesma sessão devem ser serializadas por `session_id` usando travas assíncronas (`asyncio.Lock`).
