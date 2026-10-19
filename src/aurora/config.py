"""Configurações da aplicação Aurora."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações e caminhos do sistema."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AURORA_MODEL_NAME: str = "gemini-2.5-flash"

    AURORA_HOST: str = "0.0.0.0"
    AURORA_PORT: int = 8000
    AURORA_RELOAD: bool = False

    AURORA_DB_PATH: Path = Path("./storage/aurora.db")
    AURORA_DADOS_DIR: Path = Path("./dados")

    @property
    def api_key(self) -> str:
        """Retorna a chave do Google AI Studio configurada."""
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY


settings = Settings()
