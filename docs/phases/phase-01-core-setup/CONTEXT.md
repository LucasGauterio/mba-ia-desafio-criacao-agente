# Contexto da Fase 01: Core Setup, SQLite & Reset CLI

## Resumo Técnico
Esta fase estabelece os alicerces do projeto:
- Inicialização do banco SQLite em `storage/aurora.db` com `PRAGMA journal_mode=WAL` e `PRAGMA busy_timeout=5000`.
- Definição da tabela `codigos_reserva_usados (codigo PRIMARY KEY)` para satisfazer a Regra de Negócio RN05 (unicidade perpétua mesmo após cancelamentos e reinícios).
- Definição da constraint física `UNIQUE(area, data)` na tabela `reservas` para a Garantia 5.
- Carga determinística dos JSONs de `dados/` sem alterar os arquivos base.
