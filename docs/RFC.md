# RFC: Proposta Técnica e Arquitetura do Residencial Aurora

## 1. Proposta Técnica
Implementação do assistente virtual utilizando:
- **Python 3.12+** gerenciado com **`uv`**.
- **Google ADK (Agent Development Kit) v2.2.0** como runtime de orquestração multiagente.
- **FastAPI** como camada de exposição HTTP assíncrona.
- **SQLite em disco** com WAL mode (`storage/aurora.db`) para persistência das sessões e dos dados de condomínio.

---

## 2. Padrões de Arquitetura

### 2.1. Topologia de Agentes
- `recepcao_aurora`: Agente principal de boas-vindas e triagem inicial. Não possui tools de banco de dados e não possui o regulamento em sua instrução.
- `agente_reservas`: Sub-agent especialista em reservas, equipado com `consultar_minhas_reservas`, `verificar_disponibilidade_area`, `reservar_area` e `cancelar_minha_reserva`.
- `agente_visitantes`: Sub-agent especialista em portaria, equipado com `listar_meus_visitantes` e `autorizar_visitante`.
- `agente_regulamento`: Sub-agent especialista em normas internas, equipado com `consultar_capitulo_regulamento`.

### 2.2. Mecanismo de Confirmações e Retomada
- Quando `taxa > 0` em reserva ou em autorização de visitante, `tool_context.request_confirmation(...)` pausa a execução do sub-agent.
- O `App` é configurado com `ResumabilityConfig(is_resumable=True)`.
- A rota `POST /sessoes/{id}/confirmacoes` verifica a existência da pendência (retornando `409 Conflict` se inválida) e retoma o sub-agent correspondente via `runner.run_async(...)` com o `FunctionResponse`.

### 2.3. Concorrência e Transações
- A tabela `reservas` possui restrição física `UNIQUE(area, data)`.
- As escritas ocorrem dentro de transações `BEGIN IMMEDIATE` no SQLite.
- Violações de chave única disparam `sqlite3.IntegrityError`, tratado na tool para retornar indisponibilidade graciosa (`HTTP 200`).

---

## 3. Segurança e Zero Trust
- Credenciais lidas exclusivamente de `.env` (`GOOGLE_API_KEY` ou `GEMINI_API_KEY`).
- Estado da sessão protegido: o apartamento é injetado no `state` e nunca passado como argumento de tool para o LLM.
- Consultas de agenda retornam apenas status booleano, protegendo os dados de outros apartamentos.
