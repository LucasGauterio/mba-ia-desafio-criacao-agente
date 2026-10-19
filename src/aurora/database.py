"""Gerenciamento de banco de dados SQLite, schemas, seeds e reset."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from aurora.config import settings


@contextmanager
def get_db_connection(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """Retorna uma conexão configurada com o SQLite (WAL mode, busy_timeout)."""
    path = db_path or settings.AURORA_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    """Cria as tabelas relacionais do condomínio."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS apartamentos (
            numero TEXT PRIMARY KEY,
            morador TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS areas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            taxa REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reservas (
            codigo TEXT PRIMARY KEY,
            apartamento TEXT NOT NULL,
            area TEXT NOT NULL,
            data TEXT NOT NULL,
            UNIQUE(area, data)
        );

        CREATE TABLE IF NOT EXISTS codigos_reserva_usados (
            codigo TEXT PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apartamento TEXT NOT NULL,
            nome TEXT NOT NULL,
            data TEXT NOT NULL
        );
        """
    )
    conn.commit()


def seed_initial_data(conn: sqlite3.Connection, dados_dir: Optional[Path] = None) -> None:
    """Carrega os dados iniciais a partir dos arquivos imutáveis em dados/."""
    base_dir = dados_dir or settings.AURORA_DADOS_DIR

    # 1. Apartamentos
    with open(base_dir / "apartamentos.json", "r", encoding="utf-8") as f:
        apartamentos = json.load(f)
        for apto in apartamentos:
            conn.execute(
                "INSERT OR REPLACE INTO apartamentos (numero, morador) VALUES (?, ?)",
                (apto["numero"], apto["morador"]),
            )

    # 2. Áreas Comuns
    with open(base_dir / "areas.json", "r", encoding="utf-8") as f:
        areas = json.load(f)
        for area in areas:
            conn.execute(
                "INSERT OR REPLACE INTO areas (id, nome, taxa) VALUES (?, ?, ?)",
                (area["id"], area["nome"], float(area["taxa"])),
            )

    # 3. Reservas Iniciais e Registro Histórico de Códigos
    with open(base_dir / "reservas.json", "r", encoding="utf-8") as f:
        reservas = json.load(f)
        for res in reservas:
            conn.execute(
                "INSERT OR IGNORE INTO codigos_reserva_usados (codigo) VALUES (?)",
                (res["codigo"],),
            )
            conn.execute(
                "INSERT OR REPLACE INTO reservas (codigo, apartamento, area, data) VALUES (?, ?, ?, ?)",
                (res["codigo"], res["apartamento"], res["area"], res["data"]),
            )

    # 4. Visitantes Iniciais
    with open(base_dir / "visitantes.json", "r", encoding="utf-8") as f:
        visitantes = json.load(f)
        for vis in visitantes:
            conn.execute(
                "INSERT INTO visitantes (apartamento, nome, data) VALUES (?, ?, ?)",
                (vis["apartamento"], vis["nome"], vis["data"]),
            )

    conn.commit()


def reset_database(db_path: Optional[Path] = None, dados_dir: Optional[Path] = None) -> None:
    """Limpa e recria o banco de dados exatamente no estado dos arquivos em dados/."""
    with get_db_connection(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS reservas;")
        conn.execute("DROP TABLE IF EXISTS visitantes;")
        conn.execute("DROP TABLE IF EXISTS codigos_reserva_usados;")
        conn.execute("DROP TABLE IF EXISTS areas;")
        conn.execute("DROP TABLE IF EXISTS apartamentos;")
        init_schema(conn)
        seed_initial_data(conn, dados_dir)
