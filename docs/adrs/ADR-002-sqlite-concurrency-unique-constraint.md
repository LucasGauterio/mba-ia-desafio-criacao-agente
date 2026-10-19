# ADR-002: Concorrência Atômica no SQLite com Restrição UNIQUE e Transações BEGIN IMMEDIATE

## Status
Aceito (Accepted)

## Contexto
A Garantia 5 e a Regra de Negócio RN01 exigem que cada área comum aceite no máximo uma reserva por data e que, na ocorrência de duas aprovações simultâneas disparadas em paralelo por moradores diferentes para a mesma área e data, ambas as requisições HTTP retornem `200 OK` e exatamente uma reserva seja gravada. Fazer uma simples checagem (`SELECT`) em código antes do `INSERT` é sujeito a *race conditions* (*time-of-check to time-of-use* - TOCTOU).

## Decisão
Implementamos a exclusividade física no motor relacional do SQLite:
1. **Constraint de Integridade**: A tabela `reservas` possui a restrição `UNIQUE(area, data)`.
2. **Transação Serializada**: No momento da gravação atômica da reserva (após confirmação), abrimos a transação com `BEGIN IMMEDIATE` e ativamos `PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`.
3. **Tratamento de Exceção Gracioso**: A tool captura `sqlite3.IntegrityError` gerada pela colisão da constraint `UNIQUE` e retorna um dicionário de status amigável (`status: "indisponivel"`), permitindo que a API responda com status HTTP `200 OK`.

## Consequências
- **Positivas**: Exclusividade inquebrável garantida no nível do banco de dados; imunidade contra concorrência simultânea sem necessidade de bancos de dados distribuídos complexos.
- **Negativas**: SQLite requer timeout de busy adequado em cenários de alta concorrência.
