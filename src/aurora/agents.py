"""Definição da topologia multiagente com Google ADK v2."""

from pathlib import Path
from typing import Optional

from google.adk import Agent, Runner
from google.adk.apps import App, ResumabilityConfig
from google.adk.sessions import DatabaseSessionService

from aurora.config import settings
from aurora.tools import (
    autorizar_visitante,
    cancelar_minha_reserva,
    consultar_capitulo_regulamento,
    consultar_minhas_reservas,
    listar_areas_comuns,
    listar_meus_visitantes,
    reservar_area,
    verificar_disponibilidade_area,
)

# 1. Especialista em Reservas de Áreas Comuns
agente_reservas = Agent(
    name="agente_reservas",
    model=settings.AURORA_MODEL_NAME,
    instruction=(
        "Você é o especialista em reservas de áreas comuns do Residencial Aurora. "
        "Você tem acesso às ferramentas para listar áreas comuns, verificar disponibilidade, "
        "consultar reservas do apartamento, realizar novas reservas e cancelar reservas próprias. "
        "Regras críticas de negócio:\n"
        "1. A reserva da quadra poliesportiva tem taxa R$ 0,00 e é feita imediatamente.\n"
        "2. A reserva do salão de festas ou da churrasqueira possui taxa e requer confirmação do morador. "
        "Ao solicitar a reserva de área com taxa, a ferramenta entrará em estado de confirmação.\n"
        "3. O morador pode cancelar apenas reservas do seu próprio apartamento.\n"
        "4. Nunca mencione códigos de reservas de outros apartamentos nem identifique moradores de outras unidades."
    ),
    tools=[
        listar_areas_comuns,
        consultar_minhas_reservas,
        verificar_disponibilidade_area,
        reservar_area,
        cancelar_minha_reserva,
    ],
)

# 2. Especialista em Portaria e Visitantes
agente_visitantes = Agent(
    name="agente_visitantes",
    model=settings.AURORA_MODEL_NAME,
    instruction=(
        "Você é o especialista em portaria e visitantes do Residencial Aurora. "
        "Você tem acesso às ferramentas para listar visitantes autorizados e cadastrar novas autorizações de entrada. "
        "Regras críticas:\n"
        "1. Toda autorização de visitante libera acesso físico ao condomínio e requer confirmação formal do morador pelo sistema. "
        "Mesmo que o morador diga que já confirmou na conversa, chame a ferramenta de autorização normalmente para acionar a confirmação do sistema."
    ),
    tools=[
        listar_meus_visitantes,
        autorizar_visitante,
    ],
)

# 3. Especialista em Regulamento Interno (Garantia 4)
agente_regulamento = Agent(
    name="agente_regulamento",
    model=settings.AURORA_MODEL_NAME,
    instruction=(
        "Você é o especialista no regulamento interno do Residencial Aurora. "
        "O regulamento possui 14 capítulos numerados de 1 a 14:\n"
        "- Capítulo 1: Disposições gerais\n"
        "- Capítulo 2: Direitos e deveres dos moradores\n"
        "- Capítulo 3: Silêncio e boa convivência\n"
        "- Capítulo 4: Piscina\n"
        "- Capítulo 5: Academia, brinquedoteca e playground\n"
        "- Capítulo 6: Salão de festas, churrasqueira e quadra\n"
        "- Capítulo 7: Portaria e segurança\n"
        "- Capítulo 8: Animais de estimação\n"
        "- Capítulo 9: Mudanças\n"
        "- Capítulo 10: Obras e reformas\n"
        "- Capítulo 11: Garagem e veículos\n"
        "- Capítulo 12: Coleta de lixo e reciclagem\n"
        "- Capítulo 13: Infrações e penalidades\n"
        "- Capítulo 14: Disposições finais\n\n"
        "Quando o morador fizer uma pergunta sobre normas do condomínio, identifique o número do capítulo aplicável "
        "e chame a ferramenta consultar_capitulo_regulamento para obter o texto oficial antes de responder. "
        "Por exemplo: dúvidas sobre piscina (incluindo horários aos domingos e feriados) pertencem ao Capítulo 4."
    ),
    tools=[
        consultar_capitulo_regulamento,
    ],
)

# 4. Agente Principal de Triagem / Recepção (Garantia 4: Sem regulamento na instrução)
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
    sub_agents=[
        agente_reservas,
        agente_visitantes,
        agente_regulamento,
    ],
)


def criar_app() -> App:
    """Cria a aplicação ADK com suporte a retomada de execução."""
    recepcao_aurora.sub_agents = [agente_reservas, agente_visitantes, agente_regulamento]
    return App(
        name="aurora",
        root_agent=recepcao_aurora,
        resumability_config=ResumabilityConfig(is_resumable=True),
    )


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
