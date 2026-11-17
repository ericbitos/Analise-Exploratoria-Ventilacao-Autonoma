"""Layout completo do dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd
from dash import dash_table, dcc, html

from . import data, figures
from .components import (
    badge,
    card,
    cards_recorte,
    grafico,
    kpi,
    nota,
    section_header,
    tabela,
)
from .config import (
    FONT_FAMILY,
    PHASE_NOTE,
    STATE_LABELS,
)
from .formatting import (
    fmt,
    fmt_duracao,
    fmt_hora,
    fmt_pct,
    fmt_sinal,
)
from .presentation import aba_projeto


def _linha_em(df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.Series:
    indice = (df["timestamp"] - timestamp).abs().idxmin()
    return df.loc[indice]


def _cabecalho(metricas: dict[str, Any]) -> html.Header:
    return html.Header(
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Projeto Integrador 3", className="eyebrow"),
                        html.H1("Ventilação Autônoma — Análise Exploratória"),
                        html.P(
                            "Temperatura e umidade de um ciclo único de 10 minutos "
                            "com acionamento do cooler. Explore os dados por estado "
                            "do cooler e por fase do experimento.",
                            className="subtitle",
                        ),
                    ],
                    className="header-text",
                ),
                html.Div(
                    [
                        badge(f"{metricas['leituras']} leituras"),
                        badge(f"{metricas['inicio']:%d/%m/%Y}"),
                        badge(
                            f"{fmt_hora(metricas['inicio'])} – "
                            f"{fmt_hora(metricas['fim'])}"
                        ),
                        badge("1 ciclo do cooler"),
                    ],
                    className="badges",
                ),
            ],
            className="header-inner",
        )
    )


def _aba_visao_geral() -> html.Div:
    df = data.carregar_leituras()
    metricas = data.metricas_gerais(df)
    fases = data.calcular_fases(df)
    jogo = fases[1]
    pos = fases[2]
    taxa_jogo = (jogo["temp_fim"] - jogo["temp_ini"]) / (jogo["duracao_s"] / 60)
    taxa_pos = (pos["temp_fim"] - pos["temp_ini"]) / (pos["duracao_s"] / 60)

    cartoes = html.Div(
        [
            kpi(
                str(metricas["leituras"]),
                "Leituras válidas",
                f"Cadência mediana de {fmt(metricas['intervalo_mediano'], 2)} s",
            ),
            kpi(
                fmt_duracao(metricas["duracao_s"]),
                "Duração do período",
                f"{metricas['inicio']:%d/%m/%Y} · horário local",
            ),
            kpi(
                f"{fmt(metricas['temp_max'], 1)} °C",
                "Temperatura máxima",
                f"Pico às {fmt_hora(metricas['pico_hora'])}",
            ),
            kpi(
                f"{fmt(metricas['temp_media_on'], 2)} °C",
                "Temp. média com cooler",
                (
                    f"{fmt_sinal(metricas['delta_temp'], 2)} °C vs desligado "
                    f"({fmt(metricas['temp_media_off'], 2)} °C)"
                ),
            ),
            kpi(
                f"{fmt(metricas['umi_media_on'], 2)} %",
                "Umidade média com cooler",
                (
                    f"{fmt_sinal(metricas['delta_umi'], 2)} p.p. vs desligado "
                    f"({fmt(metricas['umi_media_off'], 2)} %)"
                ),
            ),
            kpi(
                fmt(metricas["correlacao"], 3),
                "Correlação temp × umidade",
                "Pearson, todas as leituras",
            ),
        ],
        className="kpi-grid",
    )

    linhas_fases = [
        [
            fase["nome"],
            fmt_duracao(fase["duracao_s"]),
            str(fase["leituras"]),
            f"{fmt(fase['temp_media'], 2)} °C",
            f"{fmt(fase['temp_min'], 1)} – {fmt(fase['temp_max'], 1)} °C",
            f"{fmt(fase['umi_media'], 2)} %",
        ]
        for fase in fases
    ]

    achados = [
        (
            "Dois regimes bem definidos.",
            f" O cooler ligou às {fmt_hora(fases[1]['inicio'])}"
            f" e permaneceu ligado por {fmt_duracao(metricas['tempo_on_s'])}.",
        ),
        (
            "O jogo adicionou carga térmica.",
            f" A temperatura subiu de {fmt(jogo['temp_ini'], 1)} °C para "
            f"{fmt(jogo['temp_fim'], 1)} °C em {fmt_duracao(jogo['duracao_s'])}, "
            f"mesmo com o cooler ligado ({fmt_sinal(taxa_jogo, 2)} °C/min).",
        ),
        (
            "O cooler foi decisivo no pós-jogo.",
            f" Com o jogo fechado, a temperatura caiu de "
            f"{fmt(pos['temp_ini'], 1)} °C para {fmt(pos['temp_fim'], 1)} °C em "
            f"{fmt_duracao(pos['duracao_s'])} ({fmt_sinal(taxa_pos, 2)} °C/min).",
        ),
        (
            "As variáveis se movem em sentidos opostos.",
            f" A correlação de Pearson entre temperatura e umidade é "
            f"{fmt(metricas['correlacao'], 3)}.",
        ),
        (
            "Poucas transições.",
            " Houve apenas duas mudanças de estado do cooler, caracterizando "
            "um único ciclo liga–desliga.",
        ),
    ]

    return html.Div(
        [
            cartoes,
            card(
                grafico(figures.fig_visao_geral(True), id="visao-grafico"),
                titulo="Temperatura ao longo do experimento",
                descricao=(
                    "As faixas de fundo marcam as fases do experimento. "
                    "A linha é a temperatura registrada a cada ~2 s."
                ),
            ),
            html.Div(
                [
                    card(
                        tabela(
                            [
                                "Fase",
                                "Duração",
                                "Leituras",
                                "Temp. média",
                                "Temp. mín.–máx.",
                                "Umidade média",
                            ],
                            linhas_fases,
                        ),
                        titulo="Resumo por fase",
                        descricao="Médias calculadas sobre as leituras de cada fase.",
                    ),
                    card(
                        html.Ul(
                            [
                                html.Li([html.Strong(titulo), texto])
                                for titulo, texto in achados
                            ],
                            className="findings",
                        ),
                        titulo="Principais achados",
                        descricao="Números derivados das 306 leituras.",
                    ),
                ],
                className="grid-2",
            ),
            nota(PHASE_NOTE),
            nota(
                "O experimento tem apenas um ciclo de 10 minutos e não possui "
                "rodada de controle sem cooler. Os resultados são descritivos e "
                "não permitem concluir causalidade de forma generalizada."
            ),
        ],
        className="tab-body",
    )


def _aba_series(df: pd.DataFrame) -> html.Div:
    total = len(df)
    posicoes = sorted({0, total // 4, total // 2, (3 * total) // 4, total - 1})
    marcas = {pos: fmt_hora(df.loc[pos, "timestamp"]) for pos in posicoes}

    controles = html.Div(
        [
            html.Div(
                [
                    html.Label("Variável", className="control-label"),
                    dcc.Dropdown(
                        id="serie-variavel",
                        options=[
                            {"label": "Temperatura", "value": "temperatura"},
                            {"label": "Umidade", "value": "umidade"},
                            {"label": "Temperatura + umidade", "value": "ambos"},
                        ],
                        value="temperatura",
                        clearable=False,
                        className="dropdown",
                    ),
                ],
                className="control",
            ),
            html.Div(
                [
                    html.Label("Opções", className="control-label"),
                    dcc.Checklist(
                        id="serie-opcoes",
                        options=[
                            {
                                "label": "Colorir por estado do cooler",
                                "value": "colorir",
                            },
                            {"label": "Média móvel de 5 leituras", "value": "suavizar"},
                        ],
                        value=["colorir"],
                        className="checklist",
                    ),
                ],
                className="control control-opcoes",
            ),
        ],
        className="controls",
    )

    janela = html.Div(
        [
            html.Label(
                "Janela de tempo",
                className="control-label",
                id="serie-janela-label",
            ),
            dcc.RangeSlider(
                id="serie-janela",
                min=0,
                max=total - 1,
                value=[0, total - 1],
                marks=marcas,
                step=1,
                allowCross=False,
                pushable=0,
                className="slider",
            ),
        ],
        className="control control-janela",
    )

    return html.Div(
        [
            section_header(
                "Séries temporais",
                "A linha muda de cor conforme o estado do cooler. As linhas "
                "tracejadas marcam o acionamento, o pico e o desligamento.",
            ),
            card(controles, classe="controls-card"),
            card(janela, classe="controls-card"),
            card(grafico(figures.fig_serie_temporal("temperatura", True, False, [0, total - 1]), id="serie-grafico")),
            html.Div(cards_recorte(df), id="serie-stats", className="mini-grid"),
        ],
        className="tab-body",
    )


def _aba_comparacao() -> html.Div:
    df = data.carregar_leituras()
    estados = data.resumo_estado(df)

    linhas = [
        [
            linha["estado"],
            str(linha["leituras"]),
            fmt_pct(linha["percentual"], 1),
            fmt_duracao(linha["duracao_s"]),
            f"{fmt(linha['temp_media'], 2)} °C",
            f"{fmt(linha['temp_min'], 1)} – {fmt(linha['temp_max'], 1)} °C",
            f"{fmt(linha['umi_media'], 2)} %",
            f"{fmt(linha['umi_min'], 1)} – {fmt(linha['umi_max'], 1)} %",
        ]
        for linha in estados
    ]

    return html.Div(
        [
            section_header(
                "Comparação por estado do cooler",
                "Distribuições e médias das variáveis nos períodos com o cooler "
                "desligado (azul) e ligado (vermelho).",
            ),
            card(
                html.Div(
                    [
                        html.Label("Variável", className="control-label"),
                        dcc.RadioItems(
                            id="comparacao-variavel",
                            options=[
                                {"label": "Temperatura", "value": "temperatura"},
                                {"label": "Umidade", "value": "umidade"},
                            ],
                            value="temperatura",
                            className="radio",
                            inline=True,
                        ),
                    ],
                    className="control",
                ),
                classe="controls-card",
            ),
            html.Div(
                [
                    card(
                        grafico(figures.fig_box("temperatura"), id="comparacao-box"),
                        titulo="Boxplot com as leituras individuais",
                    ),
                    card(
                        grafico(figures.fig_histograma("temperatura"), id="comparacao-hist"),
                        titulo="Histograma sobreposto",
                    ),
                ],
                className="grid-2",
            ),
            card(
                tabela(
                    [
                        "Estado",
                        "Leituras",
                        "%",
                        "Tempo",
                        "Temp. média",
                        "Temp. mín.–máx.",
                        "Umidade média",
                        "Umidade mín.–máx.",
                    ],
                    linhas,
                ),
                titulo="Resumo por estado do cooler",
            ),
            card(
                grafico(figures.fig_barras_fases()),
                titulo="Médias por fase do experimento",
                descricao=(
                    "Antes, jogo, pós-jogo e após o cooler. As fases do jogo "
                    "são contexto experimental informado."
                ),
            ),
            nota(PHASE_NOTE),
        ],
        className="tab-body",
    )


def _aba_correlacoes() -> html.Div:
    return html.Div(
        [
            section_header(
                "Correlações e taxas de variação",
                "Relação entre temperatura e umidade, matriz de correlação e "
                "velocidade de mudança das variáveis.",
            ),
            html.Div(
                [
                    card(
                        grafico(figures.fig_dispersao()),
                        titulo="Temperatura × umidade",
                        descricao=(
                            "Cada ponto é uma leitura. A reta tracejada é o "
                            "ajuste linear simples."
                        ),
                    ),
                    card(
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id="correlacao-metodo",
                                    options=[
                                        {"label": "Pearson", "value": "pearson"},
                                        {"label": "Spearman", "value": "spearman"},
                                    ],
                                    value="pearson",
                                    className="radio",
                                    inline=True,
                                ),
                                grafico(
                                    figures.fig_heatmap("pearson"),
                                    id="correlacao-heatmap",
                                ),
                            ]
                        ),
                        titulo="Matriz de correlação",
                        descricao="Inclui as taxas de variação como variáveis derivadas.",
                    ),
                ],
                className="grid-2",
            ),
            card(
                html.Div(
                    [
                        html.Label(
                            "Suavização (média móvel)", className="control-label"
                        ),
                        dcc.Slider(
                            id="taxas-janela",
                            min=1,
                            max=15,
                            step=1,
                            value=5,
                            marks={1: "1", 5: "5", 10: "10", 15: "15"},
                            className="slider",
                        ),
                    ],
                    className="control control-slider",
                ),
                grafico(figures.fig_taxas(5), id="taxas-grafico"),
                titulo="Taxas de variação",
                descricao=(
                    "Diferença entre leituras consecutivas convertida para "
                    "unidade por minuto, suavizada por média móvel."
                ),
            ),
        ],
        className="tab-body",
    )


def _aba_dados(df: pd.DataFrame) -> html.Div:
    metricas = data.metricas_gerais(df)
    qualidade = data.qualidade_dados(df)

    eventos = data.calcular_eventos(df)
    marcos = [
        ("Início", eventos["inicio"]),
        ("Cooler ligou", eventos["jogo_abre"]),
        ("Pico de temperatura", eventos["pico"]),
        ("Cooler desligou", eventos["cooler_off"]),
    ]
    linhas_eventos = []
    for rotulo, timestamp in marcos:
        linha = _linha_em(df, timestamp)
        linhas_eventos.append(
            [
                rotulo,
                fmt_hora(timestamp),
                f"{fmt(linha['temperatura'], 1)} °C",
                f"{fmt(linha['umidade'], 1)} %",
            ]
        )

    registros = [
        {
            "hora": f"{linha.timestamp:%H:%M:%S}",
            "temperatura": float(linha.temperatura),
            "umidade": float(linha.umidade),
            "estado": STATE_LABELS[int(linha.cooler)],
        }
        for linha in df.itertuples()
    ]

    return html.Div(
        [
            section_header(
                "Qualidade e dados",
                "Validação dos registros, eventos do experimento e a série "
                "completa de leituras.",
            ),
            html.Div(
                [
                    card(
                        tabela(
                            ["Métrica", "Valor", "Observação"],
                            [
                                [linha["metrica"], linha["valor"], linha["observacao"]]
                                for linha in qualidade
                            ],
                        ),
                        titulo="Relatório de qualidade",
                        descricao=(
                            f"{metricas['leituras']} linhas recebidas de "
                            "ProjetoIntegrador3.leituras, todas válidas."
                        ),
                    ),
                    card(
                        tabela(
                            ["Evento", "Horário", "Temperatura", "Umidade"],
                            linhas_eventos,
                        ),
                        titulo="Eventos do experimento",
                        descricao=(
                            "Estado inicial, acionamento, pico e desligamento "
                            "do cooler."
                        ),
                    ),
                ],
                className="grid-2 grid-2-top",
            ),
            card(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    "Filtrar por estado", className="control-label"
                                ),
                                dcc.Dropdown(
                                    id="dados-filtro",
                                    options=[
                                        {"label": "Todos", "value": "todos"},
                                        {"label": "Cooler desligado", "value": "0"},
                                        {"label": "Cooler ligado", "value": "1"},
                                    ],
                                    value="todos",
                                    clearable=False,
                                    className="dropdown dropdown-small",
                                ),
                            ],
                            className="control",
                        ),
                        html.Button(
                            "Baixar CSV do recorte",
                            id="dados-download-btn",
                            n_clicks=0,
                            className="button",
                        ),
                    ],
                    className="table-controls",
                ),
                dash_table.DataTable(
                    id="dados-tabela",
                    columns=[
                        {"name": "Horário", "id": "hora"},
                        {
                            "name": "Temperatura (°C)",
                            "id": "temperatura",
                            "type": "numeric",
                            "format": {"specifier": ".2f"},
                        },
                        {
                            "name": "Umidade (%)",
                            "id": "umidade",
                            "type": "numeric",
                            "format": {"specifier": ".2f"},
                        },
                        {"name": "Estado do cooler", "id": "estado"},
                    ],
                    data=registros,
                    page_size=15,
                    page_action="native",
                    sort_action="native",
                    sort_mode="single",
                    locale_format={"decimal": ",", "grouping": "."},
                    style_as_list_view=True,
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": "#f9fafb",
                        "fontWeight": "600",
                        "fontSize": "12px",
                        "color": "#374151",
                        "borderBottom": "1px solid #e5e7eb",
                        "textAlign": "left",
                        "padding": "10px 12px",
                    },
                    style_cell={
                        "fontFamily": FONT_FAMILY,
                        "fontSize": "12.5px",
                        "color": "#111827",
                        "border": "none",
                        "borderBottom": "1px solid #f1f2f4",
                        "textAlign": "left",
                        "padding": "8px 12px",
                        "minWidth": "90px",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#fbfbfc",
                        }
                    ],
                ),
                titulo="Leituras completas",
                descricao=(
                    "Série tratada, ordenada por horário. Use o filtro para "
                    "restringir o estado do cooler."
                ),
            ),
            dcc.Download(id="dados-download"),
            nota(
                "Fonte: tabela ProjetoIntegrador3.leituras. Snapshot estático "
                "gerado por scripts/preparar_dados.py; o dashboard não acessa "
                "o banco em tempo de execução."
            ),
        ],
        className="tab-body",
    )


def layout() -> html.Div:
    df = data.carregar_leituras()
    metricas = data.metricas_gerais(df)

    abas = dcc.Tabs(
        id="abas",
        value="projeto",
        className="tabs",
        children=[
            dcc.Tab(
                label="Projeto",
                value="projeto",
                className="tab",
                selected_className="tab-selected",
                children=aba_projeto(),
            ),
            dcc.Tab(
                label="Visão geral",
                value="visao",
                className="tab",
                selected_className="tab-selected",
                children=_aba_visao_geral(),
            ),
            dcc.Tab(
                label="Séries temporais",
                value="series",
                className="tab",
                selected_className="tab-selected",
                children=_aba_series(df),
            ),
            dcc.Tab(
                label="Comparação",
                value="comparacao",
                className="tab",
                selected_className="tab-selected",
                children=_aba_comparacao(),
            ),
            dcc.Tab(
                label="Correlações",
                value="correlacoes",
                className="tab",
                selected_className="tab-selected",
                children=_aba_correlacoes(),
            ),
            dcc.Tab(
                label="Qualidade e dados",
                value="dados",
                className="tab",
                selected_className="tab-selected",
                children=_aba_dados(df),
            ),
        ],
    )

    return html.Div(
        [
            _cabecalho(metricas),
            html.Main(abas, className="main"),
            html.Footer(
                html.Div(
                    [
                        html.Span(
                            "Análise exploratória · Projeto Integrador 3",
                            className="footer-title",
                        ),
                        html.Span(
                            "Dados de um único experimento, sem inferência causal. "
                            "Horários sem fuso, como registrados no banco.",
                            className="footer-text",
                        ),
                    ],
                    className="footer-inner",
                )
            ),
        ],
        className="app",
    )
