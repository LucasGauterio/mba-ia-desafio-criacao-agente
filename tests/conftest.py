"""Fixtures compartilhadas para a suíte de testes pytest."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from aurora.api import app
from aurora.database import reset_database


@pytest.fixture(autouse=True)
def setup_test_db():
    """Garante que cada bateria de teste parta do banco de dados resetado."""
    reset_database()
    yield


@pytest_asyncio.fixture
async def client():
    """Cliente HTTP assíncrono conectado à aplicação FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as ac:
        yield ac
