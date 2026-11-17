# Dashboard — Ventilação Autônoma

Dashboard interativo em Python (Dash + Plotly) para a análise exploratória das
leituras de temperatura e umidade de um experimento com acionamento de cooler.
Projeto Integrador 3.

**Publicado em:** https://analise-ventilacao-autonoma.onrender.com

## O que o dashboard mostra

- **Projeto** — apresentação do experimento: contexto, pergunta central,
  pipeline de coleta (Arduino + DHT11 → script Python → PostgreSQL), estrutura
  da tabela `ProjetoIntegrador3.leituras`, boas práticas de acesso e os
  resultados principais com atalhos para as demais abas.
- **Visão geral** — indicadores principais (leituras, duração, pico, médias por
  estado, correlação), série de temperatura com as fases do experimento e
  resumo por fase.
- **Séries temporais** — temperatura e/ou umidade, linha colorida por estado do
  cooler, marcadores de acionamento/pico/desligamento, janela de tempo e média
  móvel.
- **Comparação** — boxplot com leituras individuais, histograma sobreposto,
  tabela por estado e médias por fase.
- **Correlações** — dispersão temperatura × umidade, matriz de Pearson ou
  Spearman e taxas de variação com suavização ajustável.
- **Qualidade e dados** — relatório de qualidade, eventos do experimento e a
  série completa com filtro e download em CSV.

As fases do jogo (abertura às 17:55:56, pico às 17:58:38 e desligamento do
cooler às 18:01:04) são derivadas das leituras e do contexto experimental
informado na apresentação. A tabela registra apenas o estado do cooler.

## Apresentação

O dashboard é a própria apresentação e fica disponível em um link público:

**https://analise-ventilacao-autonoma.onrender.com**

A aba **Projeto** foi organizada para cobrir os quatro pontos do enunciado:

| Bloco | Tempo sugerido | Conteúdo |
|---|---:|---|
| 1. Projeto | 30 s | Contexto, pergunta central e recorte do experimento |
| 2. Coleta | 45 s | Arduino + DHT11, cadência, variáveis e qualidade |
| 3. Armazenamento | 45 s | PostgreSQL, schema, tabela e acesso somente leitura |
| 4. Resultados | 3–4 min | Principais números e navegação para os gráficos |

Cada bloco tem atalhos para as abas de análise (séries temporais, comparação,
correlações e qualidade). O roteiro completo com as notas de fala está em
`reports/apresentacao/roteiro_apresentacao.md`, no projeto de análise original.

> O plano gratuito do Render hiberna após alguns minutos sem acesso. Abra o
> link 2–3 minutos antes de apresentar; o primeiro carregamento pode levar
> cerca de 50 segundos.

## Estrutura

```text
.
├── app.py                    # entrypoint (expõe `server` para gunicorn)
├── dashboard/
│   ├── __init__.py           # create_app()
│   ├── config.py             # cores, rótulos e caminhos
│   ├── data.py               # carregamento e cálculos
│   ├── figures.py            # figuras Plotly
│   ├── components.py         # cards, tabelas e notas
│   ├── layout.py             # layout e abas
│   ├── presentation.py       # aba Projeto (contexto, coleta, banco, resultados)
│   ├── callbacks.py          # interatividade
│   └── data/leituras.csv     # snapshot dos dados
├── assets/style.css          # design
├── scripts/preparar_dados.py # regenera o snapshot
└── requirements.txt
```

## Como executar

Pré-requisito: Python 3.11 ou superior.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:8050`.

## Dados

O dashboard usa um snapshot estático em `dashboard/data/leituras.csv` com 306
leituras de 12/10/2026, entre 17:52:37 e 18:02:55. Nenhuma conexão com banco é
feita em tempo de execução.

Para regenerar o snapshot a partir das saídas da análise:

```bash
python scripts/preparar_dados.py
# ou informe outro caminho:
python scripts/preparar_dados.py --origem /caminho/leituras_tratadas.csv
```

O script espera um CSV com separador `;` e decimal `,`, como o gerado por
`analise_leituras.py`, e grava o snapshot normalizado em
`dashboard/data/leituras.csv`.

## Publicação no Render

O serviço é um **Web Service** em Python, plano `free`, região `oregon`.

| Configuração | Valor |
|---|---|
| Repositório | `https://github.com/ericbitos/Analise-Exploratoria-Ventilacao-Autonoma` |
| Branch | `main` |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:server --workers 1 --threads 4 --timeout 120` |
| Variável de ambiente | `PYTHON_VERSION=3.12.7` |

O plano gratuito hiberna após alguns minutos sem acesso; o primeiro acesso
depois disso pode levar cerca de 50 segundos.

## Limitações

- A janela analisada tem apenas 10 minutos e um único ciclo do cooler.
- Não há repetição do experimento nem controle de outras variáveis ambientais.
- O platô de umidade em 10,0% e o pico de 45,0 °C podem indicar limite do sensor.
- O estudo é exploratório: não há teste de hipótese nem inferência causal.
