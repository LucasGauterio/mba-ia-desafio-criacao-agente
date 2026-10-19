"""Parser e leitor granular do regulamento interno do condomínio."""

import re
from pathlib import Path
from typing import Dict, Optional

from aurora.config import settings

ROMANOS_PARA_INT = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
    "XI": 11,
    "XII": 12,
    "XIII": 13,
    "XIV": 14,
}

INT_PARA_ROMANOS = {v: k for k, v in ROMANOS_PARA_INT.items()}


def carregar_capitulos(caminho: Optional[Path] = None) -> Dict[int, str]:
    """Carrega o arquivo de regulamento e separa em um dicionário por número do capítulo."""
    arq = caminho or (settings.AURORA_DADOS_DIR / "regulamento.md")
    if not arq.exists():
        return {}

    with open(arq, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Divide pelos cabeçalhos de capítulos: ## Capítulo <ROMANO>: <Título>
    padrao = re.compile(r"(## Capítulo\s+([IVXLCDM]+):[^\n]+)")
    partes = padrao.split(conteudo)

    capitulos: Dict[int, str] = {}
    i = 1
    while i < len(partes):
        cabecalho = partes[i].strip()
        romano = partes[i + 1].strip()
        texto_capitulo = partes[i + 2].strip() if (i + 2) < len(partes) else ""

        num_cap = ROMANOS_PARA_INT.get(romano)
        if num_cap:
            capitulos[num_cap] = f"{cabecalho}\n\n{texto_capitulo}".strip()

        i += 3

    return capitulos


def obter_capitulo(numero: int, caminho: Optional[Path] = None) -> str:
    """Retorna o texto exclusivo do capítulo solicitado."""
    capitulos = carregar_capitulos(caminho)
    return capitulos.get(
        numero,
        f"Capítulo {numero} não encontrado. O regulamento possui os capítulos 1 a 14.",
    )
