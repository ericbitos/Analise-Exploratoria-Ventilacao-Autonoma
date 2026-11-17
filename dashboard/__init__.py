"""Aplicação Dash da análise exploratória de ventilação autônoma."""

from __future__ import annotations

from dash import Dash

from .callbacks import registrar
from .config import APP_TITLE, ASSETS_DIR
from .layout import layout


def create_app() -> Dash:
    """Monta o app Dash e registra os callbacks."""
    app = Dash(
        __name__,
        title=APP_TITLE,
        update_title=None,
        assets_folder=str(ASSETS_DIR),
    )
    app.layout = layout
    registrar(app)
    return app


__all__ = ["create_app"]
