# Assistente Virtual do Residencial Aurora

Assistente virtual inteligente integrado ao aplicativo dos moradores do **Residencial Aurora**, desenvolvido em Python com **Google ADK (Agent Development Kit)** e **FastAPI**.

O sistema orquestra o atendimento conversacional via agentes autônomos para reserva de áreas comuns, cancelamentos, autorização de visitantes e dúvidas sobre o regulamento interno, assegurando deterministicamente em código as **5 Garantias Críticas de Negócio** do condomínio: *"O modelo decide o caminho, o código decide o que é permitido."*

O enunciado original com as regras completas do desafio está preservado em [`DESAFIO.md`](./DESAFIO.md). As análises aprofundadas de requisitos, arquitetura técnica e cenários de validação encontram-se em [`ANALYSIS.md`](./ANALYSIS.md), [`ARCHITECTURE.md`](./ARCHITECTURE.md) e [`TEST_PLAN.md`](./TEST_PLAN.md).

---

## 1. Arquitetura

A solução adota o padrão **Coordenador + Especialistas via Sub-Agents** nativo do Google ADK, combinando a flexibilidade de raciocínio de LLMs (família Gemini) com a segurança de *FunctionTools* estritamente determinísticas e persistência transacional em SQLite.

```mermaid
flowchart TD
    Client["Morador / Avaliador HTTP"] --> API["FastAPI (http://localhost:8000)"]

    subgraph Camada_API ["Camada de Exposição HTTP (FastAPI)"]
        R_Sessoes["POST /sessoes"]
        R_Msg["POST /sessoes/{id}/mensagens"]
        R_Conf["POST /sessoes/{id}/confirmacoes"]
        R_Evt["GET /sessoes/{id}/eventos"]
        R_Verif["GET /apartamentos/{num}/reservas | visitantes"]
    end

    API --> R_Sessoes & R_Msg & R_Conf & R_Evt & R_Verif

    subgraph Camada_ADK ["Runtime Google ADK"]
        Runner["Runner + App (is_resumable=True)"]
        SessionSvc["DatabaseSessionService (SQLite)"]
        RootAgent["Agente Principal:\nrecepcao_aurora"]
        SubReservas["Especialista:\nagente_reservas"]
        SubVisitantes["Especialista:\nagente_visitantes"]
        SubRegulamento["Especialista:\nagente_regulamento"]
    end

    R_Sessoes --> SessionSvc
    R_Evt --> SessionSvc
    R_Msg --> Runner
    R_Conf --> Runner
    Runner <--> SessionSvc
    Runner --> RootAgent

    RootAgent -->|transfer_to_agent| SubReservas
    RootAgent -->|transfer_to_agent| SubVisitantes
    RootAgent -->|transfer_to_agent| SubRegulamento

    subgraph Camada_Tools ["Tools Determinísticas"]
        T_Res["Tools de Reservas\n(listar, checar, criar, cancelar)"]
        T_Vis["Tools de Visitantes\n(listar, autorizar)"]
        T_Reg["Tool de Regulamento\n(consultar_capitulo)"]
    end

    SubReservas --> T_Res
    SubVisitantes --> T_Vis
    SubRegulamento --> T_Reg

    subgraph Camada_Dados ["Persistência Local"]
        DB[("SQLite: storage/aurora.db\n(Domínio + Sessões ADK)")]
        DadosBase["Arquivos Base: dados/\n(somente leitura)"]
    end

    T_Res --> DB
    T_Vis --> DB
    T_Reg --> DadosBase
    R_Verif --> DB
    SessionSvc --> DB
```

### Agentes, Responsabilidades, Acionamento e Motivação

| Agente | Responsabilidade | Como é Acionado | Por Quê desta Escolha? |
| :--- | :--- | :--- | :--- |
| **`recepcao_aurora`** *(Agente Principal)* | Ponto de contato inicial do morador. Faz a triagem e direcionamento da conversa para o especialista competente. Não possui tools de banco nem regras de negócio em suas instruções. | Ponto de entrada padrão configurado no `Runner` do ADK para novas mensagens. | Isola o contexto inicial, impedindo que o modelo seja sobrecarregado com regras de ferramentas de diferentes domínios ou com o regulamento do condomínio. |
| **`agente_reservas`** *(Especialista 1)* | Gestão de áreas comuns: consulta de disponibilidade, listagem de reservas do morador, agendamento de novas reservas e cancelamento. | Sub-agent invocado via transferência (`transfer_to_agent`) a partir de `recepcao_aurora`. | Concentra as tools de reserva e as validações de taxa/disponibilidade. Mantém o contexto de conversação focado na agenda de áreas comuns. |
| **`agente_visitantes`** *(Especialista 2)* | Controle de portaria: consulta de visitantes já cadastrados e emissão de novas autorizações de entrada. | Sub-agent invocado via transferência (`transfer_to_agent`) a partir de `recepcao_aurora`. | Isola o domínio de segurança física e portaria, assegurando que o fluxo de autorização exija confirmação formal do sistema. |
| **`agente_regulamento`** *(Especialista 3)* | Resposta a dúvidas e consultas sobre normas condominiais com base exclusiva no regulamento interno. | Sub-agent invocado via transferência (`transfer_to_agent`) a partir de `recepcao_aurora`. | Evita poluir as instruções de outros agentes. Possui em seu prompt apenas o índice de capítulos e consulta seletivamente trechos sob demanda via tool. |

### Por que Sub-Agents com Transferência Aberta e `is_resumable=True`?
O desafio impõe que confirmações de ações executadas por tools (Garantia 1) pausem a execução e sejam retomadas posteriormente através de uma rota HTTP específica (`POST /sessoes/{session_id}/confirmacoes`).
Ao manter `disallow_transfer_to_parent=False` (padrão) e configurar o `App` com `ResumabilityConfig(is_resumable=True)` sobre uma sessão persistida em SQLite, o `Runner` do ADK sabe exatamente qual sub-agente originou o evento `adk_request_confirmation`. Quando a resposta do morador chega pela API, o `Runner` retoma a execução diretamente no agente especialista correto (`agente_reservas` ou `agente_visitantes`), sem perdas de contexto nem falhas de direcionamento mesmo após reinícios do servidor.

---

## 2. Garantias

As cinco garantias críticas exigidas pela administração do condomínio são aplicadas deterministicamente em nível de código (Python, SQLite e runtime do ADK), nunca confiando apenas no julgamento ou nas instruções do modelo.

### Garantia 1: Cobrança ou acesso só com confirmação

- **Arquivos:** `src/aurora/tools.py` e `src/aurora/api.py`
- **Trecho no código (`src/aurora/tools.py#L121-137`, dentro de `reservar_area`):**
  ```python
  # 3. Garantia 1: Cobrança se taxa > 0
  if taxa > 0:
      conf = tool_context.tool_confirmation
      if conf is None:
          tool_context.request_confirmation(
              hint=f"Reserva do {area_nome} para {data} sujeita à taxa de R$ {taxa:.2f}.",
              payload={"acao": "reservar_area", "detalhes": {"area": area_id, "data": data}},
          )
          return {
              "status": "pendente_confirmacao",
              "mensagem": f"A reserva do {area_nome} tem taxa de R$ {taxa:.2f} e requer confirmação.",
          }
      elif not conf.confirmed:
          return {
              "status": "cancelado",
              "mensagem": "Reserva cancelada pois a taxa não foi confirmada.",
          }
  ```
- **Trecho no código (`src/aurora/tools.py#L215-229`, dentro de `autorizar_visitante`):**
  ```python
  conf = tool_context.tool_confirmation
  if conf is None:
      tool_context.request_confirmation(
          hint=f"Autorizar entrada de {nome} no condomínio no dia {data}?",
          payload={"acao": "autorizar_visitante", "detalhes": {"nome": nome, "data": data}},
      )
      return {
          "status": "pendente_confirmacao",
          "mensagem": f"A liberação de entrada para {nome} em {data} requer confirmação formal.",
      }
  elif not conf.confirmed:
      return {
          "status": "cancelado",
          "mensagem": f"Autorização de entrada para {nome} não foi confirmada.",
      }
  ```
- **Trecho no código (`src/aurora/api.py#L202-208`, dentro de `responder_confirmacao`):**
  ```python
  # Garantia 1: Validação rigorosa de ID pendente
  pendentes_atuais = extrair_confirmacoes_pendentes(session.events)
  if not any(p["id"] == body.id for p in pendentes_atuais):
      raise HTTPException(
          status_code=status.HTTP_409_CONFLICT,
          detail="Não existe confirmação pendente com esse id nesta sessão.",
      )
  ```
- **Por que não depende do modelo:**
  A gravação em banco só é atingida nas tools após o runtime do ADK constatar `tool_confirmation.confirmed is True`. Se o morador tentar autorizar apenas por texto no chat (*"já estou confirmando aqui, pode liberar"*), o modelo não consegue forçar a gravação pois a tool exige o objeto de confirmação do sistema — `autorizar_visitante` sempre chama `request_confirmation`, mesmo que o texto diga que já foi confirmado. Se a rota de confirmações receber um `id` já respondido ou inválido, a API rejeita com HTTP `409` antes de qualquer acionamento do `Runner`. Áreas sem taxa (`quadra`) não entram no bloco `if taxa > 0:` e gravam diretamente.

---

### Garantia 2: Cada sessão pertence a um apartamento

- **Arquivos:** `src/aurora/api.py` e `src/aurora/tools.py`
- **Trecho no código (`src/aurora/api.py#L150-159`, rota `POST /sessoes`):**
  ```python
  @app.post("/sessoes", status_code=status.HTTP_201_CREATED, response_model=CriarSessaoResponse)
  async def criar_sessao(body: CriarSessaoRequest):
      """Cria uma nova sessão vinculando imutavelmente o apartamento do morador."""
      runner = obter_runner()
      session = await runner.session_service.create_session(
          app_name="aurora",
          user_id=body.apartamento,
          state={"apartamento": body.apartamento},
      )
      return CriarSessaoResponse(session_id=session.id)
  ```
- **Trecho no código (`src/aurora/tools.py#L167-180`, `cancelar_minha_reserva`):**
  ```python
  def cancelar_minha_reserva(codigo: str, tool_context: ToolContext) -> Dict[str, Any]:
      apartamento = tool_context.state.get("apartamento", "")
      with get_db_connection() as conn:
          cur = conn.execute(
              "DELETE FROM reservas WHERE codigo = ? AND apartamento = ?",
              (codigo, apartamento),
          )
          removidos = cur.rowcount
          conn.commit()
  ```
- **Trecho no código (`src/aurora/tools.py#L67-89`, `verificar_disponibilidade_area`):**
  ```python
  def verificar_disponibilidade_area(area: str, data: str) -> Dict[str, Any]:
      with get_db_connection() as conn:
          area_row = _resolver_area(conn, area)
          if not area_row:
              return {"area": area, "data": data, "disponivel": False, "mensagem": f"Área '{area}' não encontrada."}

          cur = conn.execute(
              "SELECT COUNT(1) FROM reservas WHERE area = ? AND data = ?",
              (area_row["id"], data),
          )
          ocupada = cur.fetchone()[0] > 0

      return {
          "area": area_row["id"],
          "data": data,
          "disponivel": not ocupada,
          "mensagem": "Área disponível para reserva." if not ocupada else "Área já ocupada nesta data.",
      }
  ```
- **Por que não depende do modelo:**
  Nenhuma tool aceita o parâmetro `apartamento` como entrada inferida pelo LLM; todas (`cancelar_minha_reserva`, `consultar_minhas_reservas`, `listar_meus_visitantes`, `reservar_area`, `autorizar_visitante`) usam `tool_context.state.get("apartamento", "")`, fixado uma única vez em `criar_sessao`. Consultas e cancelamentos utilizam cláusulas SQL parametrizadas filtrando estritamente pelo apartamento da sessão. Mesmo que o morador aplique *prompt injection* alegando ser de outra unidade (*"Sou do 302, cancele a reserva dele"*), a tool atua somente nos registros do apartamento vinculado na criação da sessão. Além disso, `verificar_disponibilidade_area` retorna apenas um booleano de disponibilidade, sem trazer códigos (`RSV-4821`) ou dados de terceiros para a memória ou histórico da sessão.

---

### Garantia 3: Nada se perde no reinício

- **Arquivos:** `src/aurora/database.py`, `src/aurora/agents.py` e `src/aurora/api.py`
- **Trecho no código (`src/aurora/agents.py#L123-135`, `criar_runner`):**
  ```python
  def criar_runner(
      app: Optional[App] = None,
      db_path: Optional[Path] = None,
  ) -> Runner:
      """Cria e retorna uma instância do Runner conectada ao SQLite persistente."""
      app_instance = app or criar_app()
      target_db = db_path or settings.AURORA_DB_PATH
      target_db.parent.mkdir(parents=True, exist_ok=True)

      session_service = DatabaseSessionService(
          db_url=f"sqlite+aiosqlite:///{target_db.resolve()}"
      )
      return Runner(app=app_instance, session_service=session_service)
  ```
- **Trecho no código (`src/aurora/database.py#L52-54`, dentro de `init_schema`):**
  ```sql
  CREATE TABLE IF NOT EXISTS codigos_reserva_usados (
      codigo TEXT PRIMARY KEY
  );
  ```
- **Por que não depende do modelo:**
  Toda a persistência das conversas, eventos e estados do Google ADK é delegada ao `DatabaseSessionService` gravado em arquivo SQLite local (`storage/aurora.db`), recriado a cada chamada de `criar_runner()` sobre o mesmo arquivo. Paralelamente, todas as mutações de domínio (reservas criadas/canceladas, visitantes e códigos gerados) são registradas em tabelas ACID no mesmo banco. Ao reiniciar o processo da API com `Ctrl+C` + novo `uv run python -m aurora.cli run` (sem rodar o comando de restauração, que é o único que recria as tabelas do zero), os dados permanecem intactos no disco e as sessões são retomadas em seus exatos estados anteriores, validado em [`scripts/run_test_plan.sh`](./scripts/run_test_plan.sh) (CT-13).

---

### Garantia 4: O regulamento é consultado, não carregado

- **Arquivos:** `src/aurora/agents.py`, `src/aurora/regulamento.py` e `src/aurora/tools.py`
- **Trecho no código (`src/aurora/agents.py#L94-110`, `recepcao_aurora` — instrução sem o regulamento):**
  ```python
  recepcao_aurora = Agent(
      name="recepcao_aurora",
      model=settings.AURORA_MODEL_NAME,
      instruction=(
          "Você é a recepção virtual do Residencial Aurora. Seu papel é acolher o morador e transferir "
          "o atendimento para o especialista adequado de acordo com o pedido:\n"
          "- Para áreas comuns, reservas, cancelamentos ou disponibilidade de datas: transfira para 'agente_reservas'.\n"
          "- Para liberação de visitantes ou consultas da portaria: transfira para 'agente_visitantes'.\n"
          "- Para dúvidas sobre regras, normas e regulamento interno: transfira para 'agente_regulamento'.\n"
          "Transfira a conversa diretamente para o especialista sem tentar responder ou inventar regras."
      ),
      sub_agents=[agente_reservas, agente_visitantes, agente_regulamento],
  )
  ```
- **Trecho no código (`src/aurora/agents.py#L88-90`, ferramentas de `agente_regulamento` — só o índice de capítulos vai na instrução, nenhum texto do regulamento):**
  ```python
  tools=[
      consultar_capitulo_regulamento,
  ],
  ```
- **Trecho no código (`src/aurora/regulamento.py#L58-64`, `obter_capitulo`):**
  ```python
  def obter_capitulo(numero: int, caminho: Optional[Path] = None) -> str:
      """Retorna o texto exclusivo do capítulo solicitado."""
      capitulos = carregar_capitulos(caminho)
      return capitulos.get(
          numero,
          f"Capítulo {numero} não encontrado. O regulamento possui os capítulos 1 a 14.",
      )
  ```
- **Por que não depende do modelo:**
  O arquivo integral [`dados/regulamento.md`](./dados/regulamento.md) (~45 KB) jamais é concatenado no prompt do sistema nem no contexto inicial dos agentes — `recepcao_aurora` só recebe a instrução de triagem acima, e `agente_regulamento` só recebe o índice textual dos 14 capítulos na própria instrução (não o conteúdo). O acesso ao texto é intermediado exclusivamente pela tool `consultar_capitulo_regulamento` → `obter_capitulo`, que extrai apenas o capítulo solicitado (ex.: Capítulo IV para dúvidas sobre a piscina). Com isso, nenhum trecho de capítulos alheios é registrado nos eventos da sessão (`GET /sessoes/{id}/eventos`), validado em [`scripts/run_test_plan.sh`](./scripts/run_test_plan.sh) (CT-12, CT-17).

---

### Garantia 5: Dois moradores, uma reserva

- **Arquivos:** `src/aurora/database.py` e `src/aurora/tools.py`
- **Trecho no código (`src/aurora/database.py#L44-50`, dentro de `init_schema`):**
  ```sql
  CREATE TABLE IF NOT EXISTS reservas (
      codigo TEXT PRIMARY KEY,
      apartamento TEXT NOT NULL,
      area TEXT NOT NULL,
      data TEXT NOT NULL,
      UNIQUE(area, data)
  );
  ```
- **Trecho no código (`src/aurora/tools.py#L139-164`, dentro de `reservar_area`, após a confirmação):**
  ```python
  # 4. Gravação atômica com trava de concorrência (Garantia 5 & RN05)
  try:
      conn.execute("BEGIN IMMEDIATE")
      codigo = _gerar_codigo_reserva_unico(conn)
      conn.execute(
          "INSERT INTO codigos_reserva_usados (codigo) VALUES (?)",
          (codigo,),
      )
      conn.execute(
          "INSERT INTO reservas (codigo, apartamento, area, data) VALUES (?, ?, ?, ?)",
          (codigo, apartamento, area_id, data),
      )
      conn.commit()
      return {
          "status": "sucesso",
          "codigo": codigo,
          "area": area_id,
          "data": data,
          "mensagem": f"Reserva de {area_nome} confirmada com sucesso para {data}! Código: {codigo}",
      }
  except sqlite3.IntegrityError:
      conn.rollback()
      return {
          "status": "indisponivel",
          "mensagem": f"Não foi possível concluir a reserva: a área {area_nome} acabou de ser reservada para a data {data}.",
      }
  ```
- **Por que não depende do modelo:**
  A integridade não depende de uma simples conferência preliminar em código Python (a verificação de disponibilidade no passo 2 de `reservar_area` é só uma otimização, não a garantia). A exclusividade é assegurada no instante exato da gravação no banco de dados pela constraint física `UNIQUE(area, data)` e pela transação `BEGIN IMMEDIATE` no SQLite (com WAL mode, ativado em [`get_db_connection`](./src/aurora/database.py#L12-26)). Quando duas confirmações simultâneas concorrem pela mesma data, o primeiro processo efetiva a escrita e o segundo intercepta o `sqlite3.IntegrityError`, retornando uma mensagem de indisponibilidade tratada com HTTP `200 OK` — nunca `500`. Em nenhum momento o banco permite duas reservas ativas para a mesma área e data, validado contra a API real com disputa concorrente genuína (dois `curl` simultâneos) em [`scripts/run_test_plan.sh`](./scripts/run_test_plan.sh) (CT-14).

---

## 3. Como rodar

### Pré-requisitos
- **Python 3.12** ou superior instalado.
- Gerenciador de pacotes **`uv`** instalado ([instruções do uv](https://github.com/astral-sh/uv)).
- Chave de API do **Google AI Studio** com acesso aos modelos Gemini (`gemini-2.5-flash` ou compatível).

### Configuração do Ambiente e Variáveis do `.env`
1. Clone o repositório e acesse o diretório raiz:
   ```bash
   git clone <URL_DO_FORK>
   cd mba-ia-desafio-criacao-agente
   ```
2. Crie o arquivo `.env` a partir do modelo `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Preencha sua chave no `.env`:
   ```env
   # Chave de API do Google AI Studio (obrigatória)
   GOOGLE_API_KEY=sua_chave_aqui
   GEMINI_API_KEY=sua_chave_aqui

   # Configurações de execução da API
   AURORA_HOST=0.0.0.0
   AURORA_PORT=8000
   AURORA_DB_PATH=./storage/aurora.db
   ```
4. Sincronize as dependências e o ambiente virtual gerenciado pelo `uv`:
   ```bash
   uv sync
   ```

### Comando de Restauração dos Dados Iniciais
Para restaurar o banco de dados local para o estado exato dos arquivos imutáveis em [`dados/`](./dados):
```bash
uv run python -m aurora.cli reset
```
*(Ou, via script registrado: `uv run aurora-reset`)*

Esse comando recria as tabelas no SQLite e carrega os apartamentos, áreas, reservas iniciais (`RSV-1377`, `RSV-4821`, `RSV-2950`) e visitantes originais.

### Comando para Subir a API
Para iniciar o servidor HTTP da API em `http://localhost:8000`:
```bash
uv run python -m aurora.cli run
```
*(Ou diretamente via Uvicorn: `uv run uvicorn aurora.api:app --host 0.0.0.0 --port 8000`)*

### Verificação Rápida
Com a API em execução, confira o estado inicial das rotas de verificação:
```bash
# Confere a reserva inicial do apartamento 101 (RSV-1377 na quadra)
curl -s http://localhost:8000/apartamentos/101/reservas

# Confere o visitante inicial do apartamento 302 (Marina Duarte)
curl -s http://localhost:8000/apartamentos/302/visitantes
```

---

## 4. Como Testar

Há duas camadas de teste neste projeto: a suíte automatizada (unitária + integração), que **não depende de LLM real**, e o teste manual de ponta a ponta contra a aplicação em execução, que **exercita o LLM de verdade**.

### 4.1. Testes Automatizados (Unitários e de Integração)

Não exigem `GOOGLE_API_KEY`/`GEMINI_API_KEY` nem a API em execução — rodam isoladamente contra um banco SQLite local.

```bash
# Sincroniza dependências (inclui pytest, pytest-asyncio, pytest-cov, httpx)
uv sync

# Executa toda a suíte com relatório de cobertura (configurado em pyproject.toml)
uv run pytest

# Executa apenas um arquivo ou teste específico
uv run pytest tests/test_tools.py -k test_reservar_area
```

| Arquivo | Camada | O que valida |
| :--- | :--- | :--- |
| `tests/test_database.py` | Unitário | Schema, seed inicial a partir de `dados/`, constraint `UNIQUE(area, data)` e histórico perpétuo de códigos (RN05). |
| `tests/test_tools.py` | Unitário | As 5 Garantias nas *tools* determinísticas, chamadas diretamente com `tool_context` mockado (`unittest.mock.MagicMock`) — sem passar pela API ou pelo LLM. |
| `tests/test_api_contract.py` | Integração (contrato) | Status codes e formato das rotas HTTP: `201`, `404`, `409`. |
| `tests/test_api_integration.py` | Integração | Caminhos de **sucesso** de `POST /mensagens`, `POST /confirmacoes` e `GET /eventos`, mockando a fronteira do `Runner` com objetos reais `google.adk.events.Event` (sem chamar o LLM). |
| `tests/test_evaluator_flow.py` | Integração | Simulação determinística dos 15 passos do Fluxo do Avaliador, chamando as *tools* e as rotas de leitura. |

> **Por quê a suíte automatizada não chama o LLM real**: as garantias críticas de negócio são implementadas em código Python determinístico, não em comportamento de modelo — por isso podem e devem ser verificadas sem depender de uma chamada de rede não-determinística. Essa decisão, e sua limitação conhecida (o roteamento real via `transfer_to_agent` não é verificado automaticamente), está documentada em [`docs/decisions/technical-decisions-phase-05-e2e-evaluator-validation.md`](docs/decisions/technical-decisions-phase-05-e2e-evaluator-validation.md).

### 4.2. Teste Completo da Aplicação (ponta a ponta, com LLM real)

Para validar a aplicação **de fato**, incluindo o roteamento `transfer_to_agent` e as respostas reais dos agentes, é preciso uma chave de Gemini válida em `.env` (`GOOGLE_API_KEY`/`GEMINI_API_KEY`). Há duas formas:

**Automatizada (recomendado)** — [`scripts/run_test_plan.sh`](./scripts/run_test_plan.sh) executa e valida os 18 casos de teste de [`TEST_PLAN.md`](./TEST_PLAN.md) de ponta a ponta: reset, sobe a API, cria sessões, envia as mensagens reais, aprova/nega confirmações, reinicia o processo de verdade (Passo 13) e dispara a disputa concorrente real (Passo 14) — sem nenhum mock.

```bash
./scripts/run_test_plan.sh

# Para pular o kill/restart real do Passo 13 (ex.: ambientes onde matar o processo é problemático):
SKIP_RESTART=1 ./scripts/run_test_plan.sh

# Chave com quota baixa (travando com "status 000"/timeout)? Aumente a espera entre chamadas (padrão: 5s):
REQUEST_DELAY_SECONDS=10 ./scripts/run_test_plan.sh
```

> **Limitação conhecida**: mesmo com a espera configurável (`REQUEST_DELAY_SECONDS`) entre chamadas, a execução completa dos 18 casos ainda pode travar por **rate limiting/quota da chave Gemini configurada** (não um bug de código) — `POST /mensagens` para de responder dentro do timeout sem nenhuma exceção no servidor. Se isso ocorrer, aumente `REQUEST_DELAY_SECONDS`, aguarde a janela de limite de taxa resetar, ou use uma chave com quota maior. Detalhes em [`docs/decisions/technical-decisions-phase-06-test-plan-execution.md`](docs/decisions/technical-decisions-phase-06-test-plan-execution.md).

**Manual** — para inspecionar passo a passo com `curl`:

```bash
# 1. Restaure o estado inicial dos dados
uv run python -m aurora.cli reset

# 2. Suba a API em outro terminal
uv run python -m aurora.cli run

# 3. Crie uma sessão para o apartamento 101
curl -s -X POST http://localhost:8000/sessoes -H "Content-Type: application/json" \
  -d '{"apartamento": "101"}'

# 4. Envie uma mensagem real (substitua {SESSION_ID} pelo session_id retornado acima)
curl -s -X POST http://localhost:8000/sessoes/{SESSION_ID}/mensagens -H "Content-Type: application/json" \
  -d '{"texto": "Quero reservar o salão de festas para o dia 2030-06-01"}'
```

O roteiro completo com os **18 casos de teste** (os 15 passos do Fluxo do Avaliador + 3 cenários de borda) — incluindo confirmação de cobrança, autorização de visitante, consulta ao regulamento, reinício sem perda de dados e disputa concorrente — está detalhado passo a passo, com os comandos `curl` exatos e as respostas esperadas, em [`TEST_PLAN.md`](./TEST_PLAN.md).
