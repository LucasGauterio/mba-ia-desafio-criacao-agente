"""Entrypoints de linha de comando para restaurar dados e subir a API."""

import sys
import uvicorn

from aurora.config import settings
from aurora.database import reset_database


def reset() -> None:
    """Restaura o banco de dados para o estado inicial exato de dados/."""
    print("Iniciando restauração dos dados do Residencial Aurora...")
    reset_database()
    print("Banco de dados restaurado com sucesso para o estado original em dados/.")


def run() -> None:
    """Inicia o servidor FastAPI do Residencial Aurora."""
    print(f"Iniciando API do Residencial Aurora em http://{settings.AURORA_HOST}:{settings.AURORA_PORT}...")
    uvicorn.run(
        "aurora.api:app",
        host=settings.AURORA_HOST,
        port=settings.AURORA_PORT,
        reload=settings.AURORA_RELOAD,
    )


def main() -> None:
    """Ponto de entrada geral da CLI."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "reset":
            reset()
            return
        elif cmd == "run":
            run()
            return

    print("Uso: aurora [reset | run]")


if __name__ == "__main__":
    main()
