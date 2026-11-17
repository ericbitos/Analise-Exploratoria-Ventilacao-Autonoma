"""Constantes visuais e caminhos do dashboard."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent
DATA_FILE = PACKAGE_DIR / "data" / "leituras.csv"
ASSETS_DIR = PROJECT_DIR / "assets"

APP_TITLE = "Ventilação Autônoma — Análise Exploratória"

COLOR_TEXT = "#111827"
COLOR_MUTED = "#6b7280"
COLOR_BORDER = "#e5e7eb"
COLOR_GRID = "#eef0f3"

COLOR_OFF = "#1f77b4"
COLOR_ON = "#d62728"
COLOR_TEMP = "#8c2d33"
COLOR_HUMIDITY = "#315f8c"

STATE_LABELS = {0: "Cooler desligado", 1: "Cooler ligado"}
STATE_COLORS = {0: COLOR_OFF, 1: COLOR_ON}
STATE_ORDER = [STATE_LABELS[0], STATE_LABELS[1]]

PHASE_ORDER = [
    "Antes do jogo",
    "Jogo + cooler",
    "Pós-jogo + cooler",
    "Após cooler",
]
PHASE_COLORS = {
    "Antes do jogo": "#64748b",
    "Jogo + cooler": "#d62728",
    "Pós-jogo + cooler": "#d97706",
    "Após cooler": "#1f77b4",
}

PHASE_NOTE = (
    "Os horários de abertura e fechamento do jogo são contexto experimental "
    "informado na apresentação. A tabela de leituras registra apenas o estado "
    "do cooler (0/1); as fases são derivadas desses horários."
)

VARIABLE_LABELS = {
    "temperatura": "Temperatura (°C)",
    "umidade": "Umidade relativa (%)",
    "cooler": "Cooler (0/1)",
    "taxa_temperatura_c_min": "Taxa temp. (°C/min)",
    "taxa_umidade_pct_min": "Taxa umidade (%/min)",
}

FONT_FAMILY = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif"
)

PLOT_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}
