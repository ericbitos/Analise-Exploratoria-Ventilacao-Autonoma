"""Componentes visuais reutilizados no layout."""

from __future__ import annotations

from typing import Any, Sequence

from dash import dcc, html

from .config import PLOT_CONFIG


def badge(texto: str) -> html.Span:
    return html.Span(texto, className="badge")


def kpi(valor: str, rotulo: str, detalhe: str = "") -> html.Div:
    filhos: list[Any] = [html.Div(valor, className="kpi-value")]
    filhos.append(html.Div(rotulo, className="kpi-label"))
    if detalhe:
        filhos.append(html.Div(detalhe, className="kpi-detail"))
    return html.Div(filhos, className="kpi")


def kpi_mini(valor: str, rotulo: str) -> html.Div:
    return html.Div(
        [
            html.Div(valor, className="mini-value"),
            html.Div(rotulo, className="mini-label"),
        ],
        className="mini-kpi",
    )


def cards_recorte(df: Any) -> list[html.Div]:
    """Mini cartões com estatísticas da janela selecionada."""
    from .formatting import fmt

    return [
        kpi_mini(f"{fmt(df['temperatura'].mean(), 2)} °C", "Temp. média da janela"),
        kpi_mini(f"{fmt(df['temperatura'].min(), 2)} °C", "Temp. mínima"),
        kpi_mini(f"{fmt(df['temperatura'].max(), 2)} °C", "Temp. máxima"),
        kpi_mini(f"{fmt(df['umidade'].mean(), 2)} %", "Umidade média"),
        kpi_mini(f"{fmt(df['umidade'].min(), 2)} %", "Umidade mínima"),
        kpi_mini(f"{fmt(df['umidade'].max(), 2)} %", "Umidade máxima"),
    ]


def card(
    *filhos: Any,
    titulo: str | None = None,
    descricao: str | None = None,
    classe: str = "chart-card",
) -> html.Div:
    conteudo: list[Any] = []
    if titulo:
        conteudo.append(html.H3(titulo, className="card-title"))
    if descricao:
        conteudo.append(html.P(descricao, className="card-description"))
    conteudo.extend(filhos)
    return html.Div(conteudo, className=classe)


def grafico(figura: Any, id: str | None = None) -> dcc.Graph:
    propriedades: dict[str, Any] = {
        "figure": figura,
        "config": PLOT_CONFIG,
        "className": "grafico",
    }
    if id:
        propriedades["id"] = id
    return dcc.Graph(**propriedades)


def tabela(
    cabecalhos: Sequence[str],
    linhas: Sequence[Sequence[Any]],
    classe: str = "data-table",
) -> html.Div:
    return html.Div(
        html.Table(
            [
                html.Thead(html.Tr([html.Th(cab) for cab in cabecalhos])),
                html.Tbody(
                    [
                        html.Tr([html.Td(celula) for celula in linha])
                        for linha in linhas
                    ]
                ),
            ]
        ),
        className=classe,
    )


def nota(texto: str) -> html.Div:
    return html.Div(
        [html.Span("i", className="note-icon"), html.P(texto)],
        className="note",
    )


def section_header(titulo: str, descricao: str) -> html.Div:
    return html.Div(
        [
            html.H2(titulo, className="section-title"),
            html.P(descricao, className="section-description"),
        ],
        className="section-header",
    )
