"""Callbacks de interatividade do dashboard."""

from __future__ import annotations

import pandas as pd
from dash import Dash, Input, Output, State, ctx, dcc, no_update
from dash.exceptions import PreventUpdate

from . import data, figures
from .components import cards_recorte
from .config import STATE_LABELS


def _filtrar(df: pd.DataFrame, filtro: str | None) -> pd.DataFrame:
    if filtro in {"0", "1"}:
        return df[df["cooler"].eq(int(filtro))]
    return df


def _registros(df: pd.DataFrame) -> list[dict[str, object]]:
    return [
        {
            "hora": f"{linha.timestamp:%H:%M:%S}",
            "temperatura": float(linha.temperatura),
            "umidade": float(linha.umidade),
            "estado": STATE_LABELS[int(linha.cooler)],
        }
        for linha in df.itertuples()
    ]


def registrar(app: Dash) -> None:
    @app.callback(
        Output("serie-grafico", "figure"),
        Output("serie-stats", "children"),
        Input("serie-variavel", "value"),
        Input("serie-opcoes", "value"),
        Input("serie-janela", "value"),
    )
    def atualizar_serie(
        variavel: str,
        opcoes: list[str] | None,
        janela: list[int] | None,
    ) -> tuple[object, list[object]]:
        df = data.carregar_leituras()
        opcoes = opcoes or []
        inicio, fim = (0, len(df) - 1) if not janela else (janela[0], janela[1])
        recorte = df.iloc[inicio : fim + 1]
        figura = figures.fig_serie_temporal(
            variavel or "temperatura",
            "colorir" in opcoes,
            "suavizar" in opcoes,
            [inicio, fim],
        )
        return figura, cards_recorte(recorte)

    @app.callback(
        Output("comparacao-box", "figure"),
        Output("comparacao-hist", "figure"),
        Input("comparacao-variavel", "value"),
    )
    def atualizar_comparacao(variavel: str) -> tuple[object, object]:
        variavel = variavel or "temperatura"
        return figures.fig_box(variavel), figures.fig_histograma(variavel)

    @app.callback(
        Output("correlacao-heatmap", "figure"),
        Input("correlacao-metodo", "value"),
    )
    def atualizar_heatmap(metodo: str) -> object:
        return figures.fig_heatmap(metodo or "pearson")

    @app.callback(
        Output("taxas-grafico", "figure"),
        Input("taxas-janela", "value"),
    )
    def atualizar_taxas(janela: int) -> object:
        return figures.fig_taxas(int(janela or 5))

    @app.callback(
        Output("dados-tabela", "data"),
        Input("dados-filtro", "value"),
    )
    def atualizar_tabela(filtro: str) -> list[dict[str, object]]:
        df = data.carregar_leituras()
        return _registros(_filtrar(df, filtro))

    @app.callback(
        Output("dados-download", "data"),
        Input("dados-download-btn", "n_clicks"),
        State("dados-filtro", "value"),
        prevent_initial_call=True,
    )
    def baixar_csv(n_clicks: int, filtro: str) -> object:
        if not n_clicks:
            raise PreventUpdate
        df = _filtrar(data.carregar_leituras(), filtro)
        recorte = df[["timestamp", "temperatura", "umidade", "cooler"]].copy()
        recorte["estado"] = recorte["cooler"].map(STATE_LABELS)
        conteudo = "\ufeff" + recorte.to_csv(index=False, sep=";", decimal=",")
        return dcc.send_string(conteudo, "leituras_filtradas.csv")

    alvos = {
        "projeto-ir-series": "series",
        "projeto-ir-comparacao": "comparacao",
        "projeto-ir-correlacoes": "correlacoes",
        "projeto-ir-dados": "dados",
    }

    @app.callback(
        Output("abas", "value"),
        [Input(identificador, "n_clicks") for identificador in alvos],
        prevent_initial_call=True,
    )
    def navegar(*_: int) -> object:
        return alvos.get(ctx.triggered_id, no_update)
