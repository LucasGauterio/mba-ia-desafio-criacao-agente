# Regra: Concorrência Atômica no SQLite (sqlite-concurrency-atomicity)

## Diretivas Obrigatórias (Garantia 5)
1. **Unicidade Física por Restrição de Integridade**:
   - A tabela `reservas` DEVE possuir a constraint física `UNIQUE(area, data)`.
   - A validação de disponibilidade prévia não substitui a exclusividade no instante da gravação.
2. **Modo WAL e Transação Imediata**:
   - Conexões com o SQLite devem ativar WAL mode: `PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`.
   - Transações de escrita de reserva devem executar `BEGIN IMMEDIATE` para serializar o acesso à escrita.
3. **Tratamento sem Erro 500**:
   - Ao ocorrer colisão em aprovações simultâneas, o `sqlite3.IntegrityError` deve ser capturado na tool e retornar um payload de indisponibilidade normal (`status: "indisponivel"`).
   - Ambas as requisições HTTP devem responder `200 OK` para os clientes.
