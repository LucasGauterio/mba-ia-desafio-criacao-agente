# FDD: Functional Design Document — Residencial Aurora

## 1. Diagrama de Arquitetura do Sistema (C4 / Container)

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
        T_Res["Tools de Reservas"]
        T_Vis["Tools de Visitantes"]
        T_Reg["Tool de Regulamento"]
    end

    SubReservas --> T_Res
    SubVisitantes --> T_Vis
    SubRegulamento --> T_Reg

    subgraph Camada_Dados ["Persistência Local (SQLite)"]
        DB[("storage/aurora.db\n(Domínio + Sessões ADK)")]
        DadosBase["dados/\n(somente leitura)"]
    end

    T_Res --> DB
    T_Vis --> DB
    T_Reg --> DadosBase
    R_Verif --> DB
    SessionSvc --> DB
```

---

## 2. Diagrama Sequencial: Fluxo de Confirmação (Garantia 1)

```mermaid
sequenceDiagram
    participant Morador as Morador / Avaliador
    participant API as FastAPI
    participant ADK as Runner ADK
    participant Tool as Tool (reservar_area)
    participant DB as SQLite

    Morador->>API: POST /sessoes/{id}/mensagens {"texto": "Reserve o salão para 2030-04-20"}
    API->>ADK: run_async(message)
    ADK->>Tool: reservar_area(area="salao-de-festas", data="2030-04-20")
    Tool->>DB: Checa disponibilidade e taxa (taxa = 150 > 0)
    Note over Tool: tool_confirmation is None
    Tool->>ADK: request_confirmation(payload={...})
    ADK-->>API: FunctionCall(name="adk_request_confirmation", id="call_123")
    API-->>Morador: 200 OK {"confirmacoes_pendentes": [{"id": "call_123", ...}]}

    Morador->>API: POST /sessoes/{id}/confirmacoes {"id": "call_123", "confirmado": true}
    API->>API: Valida se "call_123" está pendente (se não, 409)
    API->>ADK: run_async(FunctionResponse(id="call_123", response={"confirmed": true}))
    ADK->>Tool: reservar_area(tool_confirmation.confirmed=True)
    Tool->>DB: INSERT INTO reservas com UNIQUE(area, data)
    DB-->>Tool: OK
    Tool-->>ADK: Sucesso
    ADK-->>API: Resposta confirmada
    API-->>Morador: 200 OK {"resposta": "Reserva confirmada!", "confirmacoes_pendentes": []}
```

---

## 3. Diagrama Sequencial: Concorrência Simultânea (Garantia 5)

```mermaid
sequenceDiagram
    participant Morador1 as Morador Apto 101 (S3)
    participant Morador2 as Morador Apto 201 (S4)
    participant API as FastAPI
    participant Tool as Tool (reservar_area)
    participant DB as SQLite (BEGIN IMMEDIATE)

    Note over Morador1, Morador2: Ambas sessões possuem confirmação pendente para salao-de-festas em 2030-05-11
    par Disparo Simultâneo (&)
        Morador1->>API: POST /sessoes/{S3}/confirmacoes {"id": "c1", "confirmado": true}
        Morador2->>API: POST /sessoes/{S4}/confirmacoes {"id": "c2", "confirmado": true}
    end

    API->>Tool: Executa aprovação S3
    Tool->>DB: BEGIN IMMEDIATE; INSERT INTO reservas
    DB-->>Tool: Inserção bem-sucedida! COMMIT

    API->>Tool: Executa aprovação S4
    Tool->>DB: BEGIN IMMEDIATE; INSERT INTO reservas
    DB-->>Tool: sqlite3.IntegrityError: UNIQUE constraint failed: reservas.area, reservas.data
    Tool-->>API: Captura erro -> {"status": "indisponivel", "mensagem": "Área acabou de ser reservada."}

    API-->>Morador1: 200 OK {"resposta": "Salão reservado com sucesso!"}
    API-->>Morador2: 200 OK {"resposta": "A área acabou de ser reservada por outro morador."}
```

---

## 4. Modelo Relacional de Dados (Diagrama ER)

```mermaid
erDiagram
    apartamentos {
        string numero PK
        string morador
    }
    areas {
        string id PK
        string nome
        float taxa
    }
    reservas {
        string codigo PK
        string apartamento FK
        string area FK
        string data
    }
    codigos_reserva_usados {
        string codigo PK
    }
    visitantes {
        int id PK
        string apartamento FK
        string nome
        string data
    }

    apartamentos ||--o{ reservas : "possui"
    apartamentos ||--o{ visitantes : "autoriza"
    areas ||--o{ reservas : "agendada em"
```
