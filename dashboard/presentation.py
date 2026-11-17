"""Aba inicial de apresentação do projeto.

Cobre os quatro pontos do enunciado: projeto, coleta dos dados, armazenamento
no banco e análise dos resultados. O conteúdo usa os mesmos dados do dashboard
e não adiciona dependências.
"""

from __future__ import annotations

from typing import Any

from dash import html

from . import data
from .components import card, kpi_mini, nota, section_header, tabela
from .config import PHASE_NOTE
from .formatting import fmt, fmt_duracao, fmt_hora, fmt_sinal


def _roteiro() -> html.Div:
    etapas = [
        ("1", "Projeto", "Contexto e pergunta central", "30 s"),
        ("2", "Coleta", "Sensor, cadência e qualidade", "45 s"),
        ("3", "Armazenamento", "PostgreSQL e tabela leituras", "45 s"),
        ("4", "Resultados", "Gráficos, correlações e limitações", "3–4 min"),
    ]
    return card(
        html.Div(
            [
                html.Div(
                    [
                        html.Span(numero, className="roteiro-num"),
                        html.Div(
                            [
                                html.Div(titulo, className="roteiro-titulo"),
                                html.Div(descricao, className="roteiro-desc"),
                            ]
                        ),
                        html.Span(tempo, className="roteiro-tempo"),
                    ],
                    className="roteiro-item",
                )
                for numero, titulo, descricao, tempo in etapas
            ],
            className="roteiro",
        ),
        titulo="Roteiro da apresentação",
        descricao=(
            "Quatro blocos, cerca de 6 minutos no total. O link público é "
            "https://analise-ventilacao-autonoma.onrender.com"
        ),
    )


def _fluxo() -> html.Div:
    etapas = [
        ("1", "Arduino + DHT11", "Leitura de temperatura e umidade"),
        ("2", "Script Python", "SQLAlchemy grava cada leitura"),
        ("3", "PostgreSQL", "ProjetoIntegrador3.leituras"),
        ("4", "Análise", "pandas e estatísticas descritivas"),
        ("5", "Dashboard", "Dash + Plotly, link público"),
    ]
    elementos: list[Any] = []
    for indice, (numero, titulo, descricao) in enumerate(etapas):
        elementos.append(
            html.Div(
                [
                    html.Span(numero, className="fluxo-num"),
                    html.Div(titulo, className="fluxo-titulo"),
                    html.Div(descricao, className="fluxo-desc"),
                ],
                className="fluxo-etapa",
            )
        )
        if indice < len(etapas) - 1:
            elementos.append(html.Div("→", className="fluxo-seta"))
    return html.Div(elementos, className="fluxo")


def _pergunta_central() -> html.Div:
    return html.Div(
        [
            html.Div("Pergunta central", className="pergunta-label"),
            html.P(
                "O cooler conseguiu amenizar o aquecimento e acelerar o "
                "resfriamento depois que o jogo foi fechado?",
                className="pergunta-texto",
            ),
        ],
        className="pergunta",
    )


def _secao_projeto(metricas: dict[str, Any]) -> html.Div:
    perguntas = [
        "Quanto a temperatura subiu durante o jogo?",
        "O cooler conseguiu conter o avanço do calor?",
        "Com que rapidez o computador resfriou depois do jogo?",
    ]
    cartoes = html.Div(
        [
            kpi_mini(str(metricas["leituras"]), "leituras válidas"),
            kpi_mini(fmt_duracao(metricas["duracao_s"]), "duração do período"),
            kpi_mini(f"{fmt(metricas['temp_max'], 1)} °C", "temperatura máxima"),
            kpi_mini("1", "ciclo do cooler"),
        ],
        className="projeto-mini",
    )

    return html.Div(
        [
            section_header(
                "1 · O projeto",
                "Um computador foi submetido a uma sessão de jogo. Durante a "
                "carga, o cooler foi acionado para conter o aquecimento e "
                "permaneceu ligado depois do fechamento do jogo.",
            ),
            card(
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    "A pergunta central é se o cooler cumpriu "
                                    "dois papéis: amenizar o aquecimento "
                                    "durante o jogo e acelerar a queda de "
                                    "temperatura depois que o jogo foi fechado.",
                                    className="paragrafo",
                                ),
                                _pergunta_central(),
                                html.P(
                                    "Para responder, o experimento é dividido "
                                    "em quatro fases: antes do jogo, jogo com "
                                    "cooler, pós-jogo com cooler e após o "
                                    "cooler. Assim, aquecimento e resfriamento "
                                    "não são misturados na mesma média.",
                                    className="paragrafo muted",
                                ),
                            ],
                            className="projeto-texto",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    "Recorte do experimento",
                                    className="mini-header",
                                ),
                                cartoes,
                                html.Div(
                                    "Três perguntas de análise",
                                    className="mini-header mini-header-espaco",
                                ),
                                html.Ol(
                                    [html.Li(pergunta) for pergunta in perguntas],
                                    className="perguntas",
                                ),
                            ],
                            className="projeto-lateral",
                        ),
                    ],
                    className="projeto-grid",
                ),
                titulo="Contexto e objetivo",
                descricao=(
                    "Dados de 12/10/2026, entre 17:52:37 e 18:02:55, em "
                    "horário local."
                ),
            ),
            nota(PHASE_NOTE),
        ],
        className="secao-projeto",
    )


def _secao_coleta(metricas: dict[str, Any]) -> html.Div:
    return html.Div(
        [
            section_header(
                "2 · Coleta dos dados",
                "Um Arduino com sensor DHT11 registrou temperatura e umidade "
                "durante o experimento; um script Python gravou cada leitura "
                "no PostgreSQL com SQLAlchemy.",
            ),
            card(
                _fluxo(),
                titulo="Do sensor ao dashboard",
                descricao=(
                    "Caminho completo do dado: coleta, gravação, análise e "
                    "publicação do link."
                ),
            ),
            html.Div(
                [
                    card(
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        html.Strong("Sensor: "),
                                        "DHT11 conectado a um Arduino.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Cadência: "),
                                        f"intervalo mediano de "
                                        f"{fmt(metricas['intervalo_mediano'], 2)} s "
                                        "entre leituras.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Volume: "),
                                        f"{metricas['leituras']} leituras em "
                                        f"{fmt_duracao(metricas['duracao_s'])}.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Variáveis: "),
                                        "temperatura (°C), umidade relativa (%) "
                                        "e estado do cooler (0 = desligado, "
                                        "1 = ligado).",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Gravação: "),
                                        "script Python com SQLAlchemy inseria "
                                        "cada leitura na tabela do PostgreSQL.",
                                    ]
                                ),
                            ],
                            className="lista-simples",
                        ),
                        titulo="Como a coleta foi feita",
                    ),
                    card(
                        html.Div(
                            [
                                kpi_mini("0", "valores nulos"),
                                kpi_mini("0", "timestamps duplicados"),
                                kpi_mini("0", "valores de cooler inválidos"),
                                kpi_mini("2,025–2,026 s", "intervalo entre leituras"),
                            ],
                            className="projeto-mini",
                        ),
                        html.P(
                            "A base passou por checagens de nulos, duplicatas e "
                            "domínio do cooler. O único ponto de atenção é o "
                            "platô de umidade em 10,0%.",
                            className="paragrafo muted",
                        ),
                        titulo="Qualidade dos dados",
                        descricao="306 linhas recebidas, 306 linhas válidas.",
                    ),
                ],
                className="grid-2",
            ),
            nota(
                "O DHT11 tem faixa nominal de 20–90% de umidade relativa e "
                "precisão típica de ±5% UR. As 60 leituras consecutivas em "
                "10,0% ficam abaixo dessa faixa, o que reforça o indício de "
                "limite do sensor — o valor é tratado como observação, não "
                "como medição perfeita."
            ),
        ],
        className="secao-projeto",
    )


def _secao_armazenamento() -> html.Div:
    colunas = [
        ["id", "inteiro", "Identificador sequencial da leitura"],
        ["timestamp", "timestamp", "Data e hora da leitura"],
        ["temperatura", "decimal", "Temperatura em °C"],
        ["umidade", "decimal", "Umidade relativa em %"],
        ["cooler", "inteiro", "Estado do cooler: 0 = desligado, 1 = ligado"],
    ]

    return html.Div(
        [
            section_header(
                "3 · Armazenamento no banco",
                "As leituras ficam em um banco PostgreSQL institucional, no "
                "schema ProjetoIntegrador3. A análise acessa os dados em modo "
                "somente leitura.",
            ),
            html.Div(
                [
                    card(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("schema", className="code-label"),
                                        html.Code(
                                            "ProjetoIntegrador3",
                                            className="code-value",
                                        ),
                                    ],
                                    className="code-linha",
                                ),
                                html.Div(
                                    [
                                        html.Span("tabela", className="code-label"),
                                        html.Code("leituras", className="code-value"),
                                    ],
                                    className="code-linha",
                                ),
                                html.Div(
                                    [
                                        html.Span("volume", className="code-label"),
                                        html.Span(
                                            "306 linhas · 5 colunas",
                                            className="code-texto",
                                        ),
                                    ],
                                    className="code-linha",
                                ),
                            ],
                            className="code-bloco",
                        ),
                        tabela(
                            ["Coluna", "Tipo", "Descrição"],
                            colunas,
                        ),
                        titulo="Estrutura da tabela",
                        descricao=(
                            "O campo timestamp não possui fuso horário; os "
                            "horários são exibidos como estão no banco."
                        ),
                    ),
                    card(
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        html.Strong("Acesso somente leitura: "),
                                        "a conexão usa "
                                        "default_transaction_read_only e não "
                                        "altera nenhum registro.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Credenciais protegidas: "),
                                        "usuário e senha ficam no .env, fora do "
                                        "versionamento, e não aparecem em logs.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Snapshot para publicação: "),
                                        "o dashboard público lê um CSV "
                                        "versionado com as leituras tratadas.",
                                    ]
                                ),
                                html.Li(
                                    [
                                        html.Strong("Sem banco em produção: "),
                                        "o link no Render não acessa o "
                                        "PostgreSQL em tempo de execução.",
                                    ]
                                ),
                            ],
                            className="lista-simples",
                        ),
                        titulo="Boas práticas adotadas",
                        descricao=(
                            "A análise é reproduzível e não modifica a base "
                            "institucional."
                        ),
                    ),
                ],
                className="grid-2",
            ),
            nota(
                "Por que o dashboard não consulta o banco? O PostgreSQL "
                "institucional não é exposto publicamente. O snapshot CSV "
                "garante que o link continue funcionando e que os números "
                "sejam exatamente os da análise original."
            ),
        ],
        className="secao-projeto",
    )


def _resultado(valor: str, rotulo: str, detalhe: str) -> html.Div:
    return html.Div(
        [
            html.Div(valor, className="resultado-valor"),
            html.Div(rotulo, className="resultado-rotulo"),
            html.Div(detalhe, className="resultado-detalhe"),
        ],
        className="resultado",
    )


def _botao_aba(texto: str, identificador: str) -> html.Button:
    return html.Button(
        texto,
        id=identificador,
        n_clicks=0,
        className="button button-secundario",
    )


def _secao_resultados() -> html.Div:
    fases = data.calcular_fases()
    metricas = data.metricas_gerais()
    jogo = fases[1]
    pos = fases[2]
    taxa_jogo = (jogo["temp_fim"] - jogo["temp_ini"]) / (jogo["duracao_s"] / 60)
    taxa_pos = (pos["temp_fim"] - pos["temp_ini"]) / (pos["duracao_s"] / 60)

    return html.Div(
        [
            section_header(
                "4 · Análise dos resultados",
                "Os números abaixo resumem o experimento. Use os botões para "
                "abrir os gráficos interativos de cada etapa.",
            ),
            html.Div(
                [
                    _resultado(
                        f"{fmt_sinal(jogo['temp_fim'] - jogo['temp_ini'], 1)} °C",
                        "Aquecimento durante o jogo",
                        (
                            f"de {fmt(jogo['temp_ini'], 1)} °C a "
                            f"{fmt(jogo['temp_fim'], 1)} °C em "
                            f"{fmt_duracao(jogo['duracao_s'])} "
                            f"({fmt_sinal(taxa_jogo, 2)} °C/min)"
                        ),
                    ),
                    _resultado(
                        f"{fmt_sinal(pos['temp_fim'] - pos['temp_ini'], 1)} °C",
                        "Resfriamento no pós-jogo",
                        (
                            f"de {fmt(pos['temp_ini'], 1)} °C a "
                            f"{fmt(pos['temp_fim'], 1)} °C em "
                            f"{fmt_duracao(pos['duracao_s'])} "
                            f"({fmt_sinal(taxa_pos, 2)} °C/min)"
                        ),
                    ),
                    _resultado(
                        fmt(metricas["correlacao"], 3),
                        "Correlação temp × umidade",
                        "Pearson; as variáveis se movem em sentidos opostos",
                    ),
                    _resultado(
                        str(metricas["transicoes"]),
                        "Transições do cooler",
                        (
                            f"um único ciclo liga–desliga, ligado às "
                            f"{fmt_hora(fases[1]['inicio'])}"
                        ),
                    ),
                ],
                className="resultado-grid",
            ),
            card(
                html.Div(
                    [
                        html.P(
                            "A interpretação precisa de cautela: a tabela não "
                            "registra o estado do jogo, os horários de abertura "
                            "e fechamento são contexto experimental e não houve "
                            "rodada de controle sem cooler.",
                            className="paragrafo",
                        ),
                        html.Div(
                            [
                                _botao_aba("Séries temporais", "projeto-ir-series"),
                                _botao_aba("Comparação", "projeto-ir-comparacao"),
                                _botao_aba("Correlações", "projeto-ir-correlacoes"),
                                _botao_aba(
                                    "Qualidade e dados", "projeto-ir-dados"
                                ),
                            ],
                            className="acoes",
                        ),
                    ]
                ),
                titulo="Do resultado para a interpretação",
                descricao=(
                    "O estudo é exploratório, com um ciclo de 10 minutos e sem "
                    "inferência causal."
                ),
            ),
        ],
        className="secao-projeto",
    )


def aba_projeto() -> html.Div:
    """Conteúdo completo da aba inicial."""
    metricas = data.metricas_gerais()
    return html.Div(
        [
            _roteiro(),
            _secao_projeto(metricas),
            _secao_coleta(metricas),
            _secao_armazenamento(),
            _secao_resultados(),
        ],
        className="tab-body",
    )
