"""Construção das figuras Plotly do dashboard."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import data
from .config import (
    COLOR_BORDER,
    COLOR_GRID,
    COLOR_HUMIDITY,
    COLOR_MUTED,
    COLOR_TEMP,
    COLOR_TEXT,
    FONT_FAMILY,
    PHASE_COLORS,
    STATE_COLORS,
    STATE_LABELS,
)
from .formatting import fmt, fmt_hora


def _rgba(hexadecimal: str, alpha: float) -> str:
    valor = hexadecimal.lstrip("#")
    r, g, b = int(valor[0:2], 16), int(valor[2:4], 16), int(valor[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _aplicar_layout(
    fig: go.Figure,
    altura: int = 420,
    hovermode: str = "x unified",
    mostrar_legenda: bool = True,
    margem_topo: int = 34,
) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=altura,
        separators=",.",
        margin=dict(l=10, r=10, t=margem_topo, b=10),
        font=dict(family=FONT_FAMILY, size=12, color=COLOR_TEXT),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode=hovermode,
        hoverlabel=dict(font=dict(family=FONT_FAMILY, size=12)),
        showlegend=mostrar_legenda,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=COLOR_BORDER,
        ticks="outside",
        tickcolor=COLOR_BORDER,
        tickfont=dict(size=11, color=COLOR_MUTED),
    )
    fig.update_yaxes(
        gridcolor=COLOR_GRID,
        zeroline=False,
        tickfont=dict(size=11, color=COLOR_MUTED),
        title_font=dict(size=12, color=COLOR_MUTED),
    )
    return fig


def _marcos_eventos(
    eventos: dict[str, Any],
    limites: tuple[pd.Timestamp, pd.Timestamp] | None = None,
) -> list[tuple[str, pd.Timestamp]]:
    marcos = [
        ("Ligou", eventos["jogo_abre"]),
        ("Pico", eventos["pico"]),
        ("Desligou", eventos["cooler_off"]),
    ]
    if limites:
        inicio, fim = limites
        marcos = [marco for marco in marcos if inicio <= marco[1] <= fim]
    return marcos


def _vlines_eventos(
    fig: go.Figure, marcos: list[tuple[str, pd.Timestamp]], linhas: int = 1
) -> None:
    for _, timestamp in marcos:
        for linha in range(1, linhas + 1):
            fig.add_vline(
                x=timestamp,
                line_dash="dot",
                line_color="#9ca3af",
                line_width=1,
                row=linha,
                col=1,
            )


def _anotacoes_eventos(
    fig: go.Figure, marcos: list[tuple[str, pd.Timestamp]]
) -> None:
    for rotulo, timestamp in marcos:
        fig.add_annotation(
            x=timestamp,
            y=1.0,
            xref="x",
            yref="y domain",
            text=f"{rotulo} {fmt_hora(timestamp)}",
            showarrow=False,
            yanchor="bottom",
            font=dict(size=10, color=COLOR_MUTED),
            bgcolor="rgba(255,255,255,0.85)",
            borderpad=2,
        )


def _faixas_estado(fig: go.Figure, df: pd.DataFrame, linhas: int = 1) -> None:
    for inicio, fim, estado in data.faixas_estado(df):
        for linha in range(1, linhas + 1):
            fig.add_vrect(
                x0=inicio,
                x1=fim,
                fillcolor=STATE_COLORS[estado],
                opacity=0.07,
                line_width=0,
                layer="below",
                row=linha,
                col=1,
            )


def fig_visao_geral(mostrar_fases: bool = True) -> go.Figure:
    df = data.carregar_leituras()
    eventos = data.calcular_eventos(df)
    fases = data.calcular_fases(df, eventos)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["temperatura"],
            mode="lines",
            name="Temperatura",
            line=dict(color=COLOR_TEMP, width=2),
            hovertemplate="Temperatura: %{y:.2f} °C<extra></extra>",
        )
    )

    if mostrar_fases:
        for fase in fases:
            fig.add_vrect(
                x0=fase["inicio"],
                x1=fase["fim"],
                fillcolor=PHASE_COLORS[fase["nome"]],
                opacity=0.07,
                line_width=0,
                layer="below",
            )
            fig.add_annotation(
                x=fase["inicio"] + (fase["fim"] - fase["inicio"]) / 2,
                y=1.01,
                xref="x",
                yref="y domain",
                text=fase["nome"],
                showarrow=False,
                yanchor="bottom",
                font=dict(size=10, color=PHASE_COLORS[fase["nome"]]),
            )

    fig.update_xaxes(tickformat="%H:%M:%S")
    fig.update_yaxes(title_text="Temperatura (°C)")
    _aplicar_layout(fig, altura=430, mostrar_legenda=False, margem_topo=40)
    return fig


def fig_serie_temporal(
    variavel: str,
    colorir_por_estado: bool,
    suavizar: bool,
    janela: list[int],
) -> go.Figure:
    df = data.carregar_leituras()
    inicio, fim = int(janela[0]), int(janela[1])
    recorte = df.iloc[inicio : fim + 1].reset_index(drop=True)
    eventos = data.calcular_eventos(df)
    marcos = _marcos_eventos(
        eventos, (recorte["timestamp"].min(), recorte["timestamp"].max())
    )

    if variavel == "ambos":
        colunas = ["temperatura", "umidade"]
        titulos = ["Temperatura (°C)", "Umidade relativa (%)"]
    else:
        colunas = [variavel]
        titulos = ["Temperatura (°C)" if variavel == "temperatura" else "Umidade (%)"]

    linhas = len(colunas)
    fig = make_subplots(
        rows=linhas,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.14 if linhas > 1 else 0.0,
    )

    for indice, coluna in enumerate(colunas, start=1):
        trabalho = recorte[["timestamp", "cooler", coluna]].copy()
        if suavizar:
            trabalho["_valor"] = (
                trabalho[coluna]
                .rolling(window=5, center=True, min_periods=2)
                .mean()
                .fillna(trabalho[coluna])
            )
            nome_valor = "_valor"
        else:
            nome_valor = coluna

        unidade = "°C" if coluna == "temperatura" else "%"
        hover = f"{titulos[indice - 1]}: %{{y:.2f}} {unidade}<extra></extra>"

        if colorir_por_estado:
            _faixas_estado(fig, trabalho, linhas)
            for estado in (0, 1):
                segmentos = [
                    seg
                    for seg in data.segmentos_estado(trabalho, nome_valor)
                    if seg["cooler"] == estado
                ]
                for numero, segmento in enumerate(segmentos):
                    fig.add_trace(
                        go.Scatter(
                            x=segmento["x"],
                            y=segmento["y"],
                            mode="lines",
                            name=STATE_LABELS[estado],
                            legendgroup=str(estado),
                            showlegend=(indice == 1 and numero == 0),
                            line=dict(color=STATE_COLORS[estado], width=2.2),
                            hovertemplate=hover,
                        ),
                        row=indice,
                        col=1,
                    )
        else:
            cor = COLOR_TEMP if coluna == "temperatura" else COLOR_HUMIDITY
            fig.add_trace(
                go.Scatter(
                    x=trabalho["timestamp"],
                    y=trabalho[nome_valor],
                    mode="lines",
                    name=titulos[indice - 1],
                    line=dict(color=cor, width=1.8),
                    hovertemplate=hover,
                    showlegend=False,
                ),
                row=indice,
                col=1,
            )

        fig.update_yaxes(title_text=titulos[indice - 1], row=indice, col=1)

    _vlines_eventos(fig, marcos, linhas)
    _anotacoes_eventos(fig, marcos)
    fig.update_xaxes(
        tickformat="%H:%M:%S",
        range=[recorte["timestamp"].min(), recorte["timestamp"].max()],
        row=linhas,
        col=1,
    )
    _aplicar_layout(
        fig,
        altura=460 if linhas == 1 else 600,
        mostrar_legenda=colorir_por_estado,
        margem_topo=46 if linhas > 1 else 40,
    )
    return fig


def fig_box(variavel: str) -> go.Figure:
    df = data.carregar_leituras()
    rotulo = "Temperatura (°C)" if variavel == "temperatura" else "Umidade relativa (%)"
    unidade = "°C" if variavel == "temperatura" else "%"

    fig = go.Figure()
    for estado in (0, 1):
        grupo = df[df["cooler"].eq(estado)]
        fig.add_trace(
            go.Box(
                x=[STATE_LABELS[estado]] * len(grupo),
                y=grupo[variavel],
                name=STATE_LABELS[estado],
                marker=dict(
                    color=STATE_COLORS[estado],
                    size=3,
                    opacity=0.35,
                ),
                line=dict(color=STATE_COLORS[estado], width=1.4),
                fillcolor=_rgba(STATE_COLORS[estado], 0.12),
                boxpoints="all",
                jitter=0.45,
                pointpos=0,
                showlegend=False,
                hovertemplate=(
                    f"{rotulo}: %{{y:.2f}} {unidade}<extra></extra>"
                ),
            )
        )

    fig.update_yaxes(title_text=rotulo)
    _aplicar_layout(fig, altura=420, hovermode="closest", mostrar_legenda=False)
    return fig


def fig_histograma(variavel: str) -> go.Figure:
    df = data.carregar_leituras()
    rotulo = "Temperatura (°C)" if variavel == "temperatura" else "Umidade relativa (%)"

    fig = go.Figure()
    for estado in (0, 1):
        grupo = df[df["cooler"].eq(estado)]
        fig.add_trace(
            go.Histogram(
                x=grupo[variavel],
                name=STATE_LABELS[estado],
                marker=dict(color=STATE_COLORS[estado]),
                opacity=0.55,
                nbinsx=18,
                hovertemplate="%{y} leituras<extra></extra>",
            )
        )

    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title_text=rotulo)
    fig.update_yaxes(title_text="Leituras")
    _aplicar_layout(fig, altura=420, hovermode="closest")
    return fig


def fig_barras_fases() -> go.Figure:
    fases = data.calcular_fases()
    nomes = ["Antes", "Jogo", "Pós-jogo", "Após"]
    cores = [PHASE_COLORS[fase["nome"]] for fase in fases]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Temperatura média (°C)", "Umidade média (%)"),
        horizontal_spacing=0.12,
    )

    for coluna, chave, casas in (
        (1, "temp_media", 2),
        (2, "umi_media", 2),
    ):
        valores = [fase[chave] for fase in fases]
        fig.add_trace(
            go.Bar(
                x=nomes,
                y=valores,
                marker_color=cores,
                text=[fmt(valor, casas) for valor in valores],
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{x}: %{y:.2f}<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=coluna,
        )
        fig.update_yaxes(
            range=[0, max(valores) * 1.18],
            row=1,
            col=coluna,
        )

    _aplicar_layout(fig, altura=400, hovermode="closest", mostrar_legenda=False, margem_topo=46)
    return fig


def fig_dispersao() -> go.Figure:
    df = data.carregar_leituras()
    correlacao = float(df["temperatura"].corr(df["umidade"]))

    fig = go.Figure()
    for estado in (0, 1):
        grupo = df[df["cooler"].eq(estado)]
        fig.add_trace(
            go.Scatter(
                x=grupo["temperatura"],
                y=grupo["umidade"],
                mode="markers",
                name=STATE_LABELS[estado],
                marker=dict(
                    color=STATE_COLORS[estado],
                    size=5,
                    opacity=0.7,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    "Temperatura: %{x:.2f} °C<br>"
                    "Umidade: %{y:.2f} %<extra></extra>"
                ),
            )
        )

    coeficientes = np.polyfit(df["temperatura"], df["umidade"], 1)
    x_reta = np.linspace(df["temperatura"].min(), df["temperatura"].max(), 50)
    y_reta = np.polyval(coeficientes, x_reta)
    fig.add_trace(
        go.Scatter(
            x=x_reta,
            y=y_reta,
            mode="lines",
            name="Tendência",
            line=dict(color="#374151", width=1.4, dash="dash"),
            hoverinfo="skip",
        )
    )

    fig.add_annotation(
        x=0.02,
        y=0.97,
        xref="paper",
        yref="paper",
        text=f"Pearson r = {fmt(correlacao, 3)}",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        font=dict(size=12, color=COLOR_TEXT),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor=COLOR_BORDER,
        borderwidth=1,
        borderpad=5,
    )

    fig.update_xaxes(title_text="Temperatura (°C)")
    fig.update_yaxes(title_text="Umidade relativa (%)")
    _aplicar_layout(fig, altura=470, hovermode="closest")
    return fig


def fig_heatmap(metodo: str) -> go.Figure:
    tabela = data.correlacoes(metodo)
    rotulos = list(tabela.columns)
    texto = [[fmt(valor, 2) for valor in linha] for linha in tabela.values]

    fig = go.Figure(
        go.Heatmap(
            z=tabela.values,
            x=rotulos,
            y=rotulos,
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale="RdBu",
            reversescale=True,
            text=texto,
            texttemplate="%{text}",
            textfont=dict(size=10, color=COLOR_TEXT),
            hovertemplate="%{y} × %{x}: %{z:.3f}<extra></extra>",
            colorbar=dict(
                title=dict(text=metodo.capitalize(), side="right"),
                thickness=12,
                len=0.8,
                tickfont=dict(size=10, color=COLOR_MUTED),
            ),
            xgap=2,
            ygap=2,
        )
    )

    fig.update_xaxes(tickangle=-25, tickfont=dict(size=9, color=COLOR_MUTED))
    fig.update_yaxes(tickfont=dict(size=9, color=COLOR_MUTED), autorange="reversed")
    _aplicar_layout(fig, altura=470, hovermode="closest", mostrar_legenda=False)
    return fig


def fig_taxas(janela: int) -> go.Figure:
    df = data.carregar_leituras()
    eventos = data.calcular_eventos(df)
    suave = data.taxas_suavizadas(df, janela)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.14,
        subplot_titles=(
            "Taxa de variação da temperatura (°C/min)",
            "Taxa de variação da umidade (%/min)",
        ),
    )

    for linha, coluna, titulo in (
        (1, "taxa_temperatura", "Taxa (°C/min)"),
        (2, "taxa_umidade", "Taxa (%/min)"),
    ):
        fig.add_trace(
            go.Scatter(
                x=suave["timestamp"],
                y=suave[coluna],
                mode="lines",
                name="Média móvel",
                line=dict(color="#374151", width=1.5),
                hovertemplate="%{y:.2f}<extra></extra>",
                showlegend=False,
            ),
            row=linha,
            col=1,
        )
        fig.add_hline(
            y=0,
            line_color="#9ca3af",
            line_width=1,
            row=linha,
            col=1,
        )
        fig.update_yaxes(title_text=titulo, row=linha, col=1)

    _vlines_eventos(fig, _marcos_eventos(eventos), linhas=2)
    fig.update_xaxes(tickformat="%H:%M:%S", row=2, col=1)
    _aplicar_layout(fig, altura=560, hovermode="x unified", mostrar_legenda=False)
    return fig
