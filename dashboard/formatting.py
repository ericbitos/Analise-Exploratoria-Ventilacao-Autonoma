"""Formatação de números e datas no padrão brasileiro."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def fmt(valor: Any, casas: int = 2, sufixo: str = "") -> str:
    """Formata um número com vírgula decimal."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    if isinstance(valor, (int,)) and not isinstance(valor, bool):
        texto = f"{valor:,}".replace(",", ".")
        return f"{texto}{sufixo}"
    texto = f"{float(valor):.{casas}f}".replace(".", ",")
    return f"{texto}{sufixo}"


def fmt_int(valor: Any) -> str:
    if valor is None:
        return "—"
    return f"{int(valor):,}".replace(",", ".")


def fmt_pct(valor: float, casas: int = 1) -> str:
    return f"{fmt(valor, casas)}%"


def fmt_sinal(valor: float, casas: int = 2, sufixo: str = "") -> str:
    texto = fmt(valor, casas)
    if valor > 0:
        return f"+{texto}{sufixo}"
    return f"{texto}{sufixo}"


def fmt_hora(timestamp: pd.Timestamp) -> str:
    return pd.Timestamp(timestamp).strftime("%H:%M:%S")


def fmt_data_hora(timestamp: pd.Timestamp) -> str:
    return pd.Timestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")


def fmt_duracao(segundos: float) -> str:
    total = int(round(float(segundos)))
    minutos, seg = divmod(total, 60)
    if minutos >= 60:
        horas, minutos = divmod(minutos, 60)
        return f"{horas} h {minutos} min {seg:02d} s"
    return f"{minutos} min {seg:02d} s"
