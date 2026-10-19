"""Camada de exposição HTTP com FastAPI implementando o contrato do Residencial Aurora."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from google.adk import Runner
from google.genai.types import Content, FunctionResponse, Part
from pydantic import BaseModel, Field

from aurora.agents import criar_runner
from aurora.database import get_db_connection, init_schema, seed_initial_data

# Lock por sessão para serializar requisições concorrentes na mesma conversa
_session_locks: Dict[str, asyncio.Lock] = {}
_global_runner: Optional[Runner] = None


def obter_runner() -> Runner:
    """Retorna o Runner singleton inicializado."""
    global _global_runner
    if _global_runner is None:
        _global_runner = criar_runner()
    return _global_runner


async def obter_sessao_por_id(runner: Runner, session_id: str):
    """Localiza a sessão no banco de dados e recupera através do serviço de sessão do ADK."""
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT user_id FROM sessions WHERE id = ? AND app_name = 'aurora'",
            (session_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        user_id = row["user_id"]

    return await runner.session_service.get_session(
        app_name="aurora",
        user_id=user_id,
        session_id=session_id,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco de dados e o runtime do ADK na inicialização da API."""
    with get_db_connection() as conn:
        init_schema(conn)
        cur = conn.execute("SELECT COUNT(1) FROM apartamentos")
        if cur.fetchone()[0] == 0:
            seed_initial_data(conn)
    obter_runner()
    yield


app = FastAPI(
    title="Residencial Aurora - API",
    version="0.1.0",
    lifespan=lifespan,
)


# --- Modelos Pydantic de Entrada e Saída ---


class CriarSessaoRequest(BaseModel):
    apartamento: str


class CriarSessaoResponse(BaseModel):
    session_id: str


class MensagemRequest(BaseModel):
    texto: str


class ItemConfirmacao(BaseModel):
    id: str
    acao: str
    detalhes: Dict[str, Any] = Field(default_factory=dict)


class MensagemResponse(BaseModel):
    resposta: str
    confirmacoes_pendentes: List[ItemConfirmacao] = Field(default_factory=list)


class ConfirmacaoRequest(BaseModel):
    id: str
    confirmado: bool


# --- Funções Auxiliares de Eventos e Confirmações ---


def extrair_confirmacoes_pendentes(events: list) -> List[Dict[str, Any]]:
    """Inspeciona os eventos da sessão e identifica FunctionCalls de adk_request_confirmation pendentes."""
    chamadas: Dict[str, Dict[str, Any]] = {}
    respondidas = set()

    for evt in events:
        content = getattr(evt, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", []) or []
        for part in parts:
            fn_call = getattr(part, "function_call", None)
            if fn_call and fn_call.name == "adk_request_confirmation":
                args = fn_call.args or {}
                payload = args.get("payload") if isinstance(args.get("payload"), dict) else args
                chamadas[fn_call.id] = {
                    "id": fn_call.id,
                    "acao": payload.get("acao", "confirmar_acao"),
                    "detalhes": payload.get("detalhes", {}),
                }

            fn_resp = getattr(part, "function_response", None)
            if fn_resp:
                respondidas.add(fn_resp.id)

    pendentes = [item for cid, item in chamadas.items() if cid not in respondidas]
    return pendentes


def extrair_texto_resposta(events_gerados: list) -> str:
    """Extrai o texto final de resposta gerado pelo modelo na interação."""
    textos = []
    for evt in events_gerados:
        content = getattr(evt, "content", None)
        if content and getattr(content, "role", "") == "model":
            for part in getattr(content, "parts", []) or []:
                texto = getattr(part, "text", "")
                if texto:
                    textos.append(texto.strip())
    return " ".join(textos).strip()


# --- Rotas da API (Contrato Oficial) ---


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


@app.post("/sessoes/{session_id}/mensagens", response_model=MensagemResponse)
async def enviar_mensagem(session_id: str, body: MensagemRequest):
    """Envia uma mensagem do morador para o assistente."""
    runner = obter_runner()
    session = await obter_sessao_por_id(runner, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada.")

    lock = _session_locks.setdefault(session_id, asyncio.Lock())
    async with lock:
        user_msg = Content(role="user", parts=[Part.from_text(text=body.texto)])
        events_novos = []
        async for evt in runner.run_async(
            user_id=session.user_id,
            session_id=session_id,
            new_message=user_msg,
        ):
            events_novos.append(evt)

        sessao_atualizada = await obter_sessao_por_id(runner, session_id)
        pendentes_raw = extrair_confirmacoes_pendentes(sessao_atualizada.events)
        pendentes = [ItemConfirmacao(**p) for p in pendentes_raw]
        resposta_texto = extrair_texto_resposta(events_novos)

        return MensagemResponse(
            resposta=resposta_texto,
            confirmacoes_pendentes=pendentes,
        )


@app.post("/sessoes/{session_id}/confirmacoes", response_model=MensagemResponse)
async def responder_confirmacao(session_id: str, body: ConfirmacaoRequest):
    """Responde a uma confirmação pendente da sessão (aprovação ou negação)."""
    runner = obter_runner()
    session = await obter_sessao_por_id(runner, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada.")

    lock = _session_locks.setdefault(session_id, asyncio.Lock())
    async with lock:
        # Garantia 1: Validação rigorosa de ID pendente
        pendentes_atuais = extrair_confirmacoes_pendentes(session.events)
        if not any(p["id"] == body.id for p in pendentes_atuais):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não existe confirmação pendente com esse id nesta sessão.",
            )

        resp_msg = Content(
            role="user",
            parts=[
                Part(
                    function_response=FunctionResponse(
                        name="adk_request_confirmation",
                        id=body.id,
                        response={"confirmed": body.confirmado},
                    )
                )
            ],
        )

        events_novos = []
        async for evt in runner.run_async(
            user_id=session.user_id,
            session_id=session_id,
            new_message=resp_msg,
        ):
            events_novos.append(evt)

        sessao_atualizada = await obter_sessao_por_id(runner, session_id)
        pendentes_raw = extrair_confirmacoes_pendentes(sessao_atualizada.events)
        pendentes = [ItemConfirmacao(**p) for p in pendentes_raw]
        resposta_texto = extrair_texto_resposta(events_novos)

        return MensagemResponse(
            resposta=resposta_texto,
            confirmacoes_pendentes=pendentes,
        )


@app.get("/sessoes/{session_id}/eventos")
async def obter_eventos_sessao(session_id: str):
    """Retorna todos os eventos gravados na sessão em ordem cronológica com conteúdo completo."""
    runner = obter_runner()
    session = await obter_sessao_por_id(runner, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada.")

    return [evt.model_dump(mode="json") for evt in session.events]


# --- Rotas de Verificação Administrativa (Sem passar pelo LLM) ---


@app.get("/apartamentos/{numero}/reservas")
def listar_reservas_apartamento(numero: str):
    """Consulta diretamente o banco de dados para listar as reservas ativas do apartamento."""
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT codigo, area, data FROM reservas WHERE apartamento = ? ORDER BY data ASC",
            (numero,),
        )
        return [dict(row) for row in cur.fetchall()]


@app.get("/apartamentos/{numero}/visitantes")
def listar_visitantes_apartamento(numero: str):
    """Consulta diretamente o banco de dados para listar os visitantes autorizados pelo apartamento."""
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT nome, data FROM visitantes WHERE apartamento = ? ORDER BY data ASC",
            (numero,),
        )
        return [dict(row) for row in cur.fetchall()]
