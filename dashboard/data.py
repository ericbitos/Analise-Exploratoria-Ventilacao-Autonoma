"""Carregamento dos dados e cálculos exibidos no dashboard.

Os dados vêm de ``dashboard/data/leituras.csv``, um snapshot versionado do
arquivo ``reports/tabelas/leituras_tratadas.csv`` produzido por
``analise_leituras.py``. Nenhuma conexão com banco é feita em tempo de execução.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

from .config import DATA_FILE, VARIABLE_LABELS


@lru_cache(maxsize=1)
def carregar_leituras() -> pd.DataFrame:
    """Lê o snapshot e devolve as leituras ordenadas por horário."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Snapshot não encontrado: {DATA_FILE}. "
            "Execute 'python scripts/preparar_dados.py'."
        )
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["cooler"] = df["cooler"].astype(int)
    df["estado"] = df["cooler"].map({0: "Cooler desligado", 1: "Cooler ligado"})
    return df


def calcular_eventos(df: pd.DataFrame | None = None) -> dict[str, pd.Timestamp]:
    """Deriva os eventos do experimento a partir das próprias leituras."""
    df = carregar_leituras() if df is None else df
    ligados = df[df["cooler"].eq(1)]
    if ligados.empty:
        raise ValueError("Não há leituras com o cooler ligado.")

    jogo_abre = ligados["timestamp"].min()
    pico = df.loc[df["temperatura"].idxmax(), "timestamp"]
    depois = df[df["timestamp"].gt(pico) & df["cooler"].eq(0)]
    if depois.empty:
        raise ValueError("Não foi encontrado o desligamento do cooler.")

    return {
        "inicio": df["timestamp"].min(),
        "jogo_abre": jogo_abre,
        "pico": pico,
        "cooler_off": depois["timestamp"].min(),
        "fim": df["timestamp"].max(),
    }


def _linha_em(df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.Series:
    indice = (df["timestamp"] - timestamp).abs().idxmin()
    return df.loc[indice]


def _estatisticas_fase(
    df: pd.DataFrame,
    nome: str,
    inicio: pd.Timestamp,
    fim: pd.Timestamp,
    *,
    incluir_inicio: bool = True,
    incluir_fim: bool = True,
) -> dict[str, Any]:
    condicao = pd.Series(True, index=df.index)
    if incluir_inicio:
        condicao &= df["timestamp"].ge(inicio)
    else:
        condicao &= df["timestamp"].gt(inicio)
    if incluir_fim:
        condicao &= df["timestamp"].le(fim)
    else:
        condicao &= df["timestamp"].lt(fim)

    grupo = df[condicao]
    if grupo.empty:
        raise ValueError(f"Fase sem leituras: {nome}")

    return {
        "nome": nome,
        "inicio": inicio,
        "fim": fim,
        "leituras": len(grupo),
        "duracao_s": (fim - inicio).total_seconds(),
        "temp_ini": float(grupo["temperatura"].iloc[0]),
        "temp_fim": float(grupo["temperatura"].iloc[-1]),
        "temp_media": float(grupo["temperatura"].mean()),
        "temp_min": float(grupo["temperatura"].min()),
        "temp_max": float(grupo["temperatura"].max()),
        "umi_ini": float(grupo["umidade"].iloc[0]),
        "umi_fim": float(grupo["umidade"].iloc[-1]),
        "umi_media": float(grupo["umidade"].mean()),
        "umi_min": float(grupo["umidade"].min()),
        "umi_max": float(grupo["umidade"].max()),
    }


def calcular_fases(
    df: pd.DataFrame | None = None,
    eventos: dict[str, pd.Timestamp] | None = None,
) -> list[dict[str, Any]]:
    """Divide o experimento nas quatro fases usadas na apresentação."""
    df = carregar_leituras() if df is None else df
    ev = calcular_eventos(df) if eventos is None else eventos

    antes = _estatisticas_fase(
        df, "Antes do jogo", ev["inicio"], ev["jogo_abre"], incluir_fim=False
    )
    jogo = _estatisticas_fase(df, "Jogo + cooler", ev["jogo_abre"], ev["pico"])
    pos = _estatisticas_fase(
        df,
        "Pós-jogo + cooler",
        ev["pico"],
        ev["cooler_off"],
        incluir_inicio=False,
    )
    depois = _estatisticas_fase(
        df, "Após cooler", ev["cooler_off"], ev["fim"], incluir_inicio=False
    )

    pico = _linha_em(df, ev["pico"])
    desligamento = _linha_em(df, ev["cooler_off"])
    pos.update(
        temp_ini=float(pico["temperatura"]),
        umi_ini=float(pico["umidade"]),
        temp_fim=float(desligamento["temperatura"]),
        umi_fim=float(desligamento["umidade"]),
    )
    depois.update(
        temp_ini=float(desligamento["temperatura"]),
        umi_ini=float(desligamento["umidade"]),
    )

    return [antes, jogo, pos, depois]


def resumo_estado(df: pd.DataFrame | None = None) -> list[dict[str, Any]]:
    """Estatísticas descritivas separadas pelo estado do cooler."""
    df = carregar_leituras() if df is None else df
    total = len(df)
    linhas: list[dict[str, Any]] = []
    for estado in (0, 1):
        grupo = df[df["cooler"].eq(estado)]
        if grupo.empty:
            continue
        linhas.append(
            {
                "cooler": estado,
                "estado": "Cooler desligado" if estado == 0 else "Cooler ligado",
                "leituras": len(grupo),
                "percentual": len(grupo) / total * 100,
                "duracao_s": float(grupo["dt_s"].sum()),
                "temp_media": float(grupo["temperatura"].mean()),
                "temp_mediana": float(grupo["temperatura"].median()),
                "temp_desvio": float(grupo["temperatura"].std()),
                "temp_min": float(grupo["temperatura"].min()),
                "temp_max": float(grupo["temperatura"].max()),
                "umi_media": float(grupo["umidade"].mean()),
                "umi_mediana": float(grupo["umidade"].median()),
                "umi_desvio": float(grupo["umidade"].std()),
                "umi_min": float(grupo["umidade"].min()),
                "umi_max": float(grupo["umidade"].max()),
            }
        )
    return linhas


def metricas_gerais(df: pd.DataFrame | None = None) -> dict[str, Any]:
    """Números exibidos nos cartões da visão geral."""
    df = carregar_leituras() if df is None else df
    ev = calcular_eventos(df)
    ligado = df["cooler"].eq(1)
    desligado = ~ligado
    pico = df.loc[df["temperatura"].idxmax()]
    umidade_min = df.loc[df["umidade"].idxmin()]

    temp_on = float(df.loc[ligado, "temperatura"].mean())
    temp_off = float(df.loc[desligado, "temperatura"].mean())
    umi_on = float(df.loc[ligado, "umidade"].mean())
    umi_off = float(df.loc[desligado, "umidade"].mean())

    return {
        "leituras": len(df),
        "inicio": ev["inicio"],
        "fim": ev["fim"],
        "duracao_s": (ev["fim"] - ev["inicio"]).total_seconds(),
        "intervalo_mediano": float(df["dt_s"].median()),
        "intervalo_min": float(df["dt_s"].min()),
        "intervalo_max": float(df["dt_s"].max()),
        "temp_min": float(df["temperatura"].min()),
        "temp_max": float(df["temperatura"].max()),
        "temp_media": float(df["temperatura"].mean()),
        "pico_hora": ev["pico"],
        "umi_min": float(df["umidade"].min()),
        "umi_min_hora": umidade_min["timestamp"],
        "umi_max": float(df["umidade"].max()),
        "umi_media": float(df["umidade"].mean()),
        "correlacao": float(df["temperatura"].corr(df["umidade"])),
        "temp_media_on": temp_on,
        "temp_media_off": temp_off,
        "delta_temp": temp_on - temp_off,
        "umi_media_on": umi_on,
        "umi_media_off": umi_off,
        "delta_umi": umi_on - umi_off,
        "tempo_on_s": float(df.loc[ligado, "dt_s"].sum()),
        "tempo_off_s": float(df.loc[desligado, "dt_s"].sum()),
        "transicoes": int(df["cooler"].ne(df["cooler"].shift()).sum() - 1),
        "pico_valor": float(pico["temperatura"]),
    }


def _maior_sequencia(mascara: pd.Series) -> int:
    if mascara.empty or not mascara.any():
        return 0
    grupos = mascara.ne(mascara.shift()).cumsum()
    return int(mascara.groupby(grupos).sum().max())


def qualidade_dados(df: pd.DataFrame | None = None) -> list[dict[str, Any]]:
    """Métricas de qualidade exibidas na aba de dados."""
    df = carregar_leituras() if df is None else df
    duplicados_timestamp = int(df["timestamp"].duplicated().sum())
    duplicados_linhas = int(
        df.duplicated(subset=["timestamp", "temperatura", "umidade", "cooler"]).sum()
    )
    return [
        {
            "metrica": "Linhas recebidas / válidas",
            "valor": f"{len(df)} / {len(df)}",
            "observacao": "Nenhuma linha removida na limpeza.",
        },
        {
            "metrica": "Valores nulos",
            "valor": "0",
            "observacao": "Sem nulos em timestamp, temperatura, umidade ou cooler.",
        },
        {
            "metrica": "Timestamps duplicados",
            "valor": str(duplicados_timestamp),
            "observacao": "Nenhum horário repetido.",
        },
        {
            "metrica": "Linhas duplicadas",
            "valor": str(duplicados_linhas),
            "observacao": "Comparação por timestamp + medidas.",
        },
        {
            "metrica": "Valores de cooler fora de 0/1",
            "valor": "0",
            "observacao": "Somente os estados desligado (0) e ligado (1).",
        },
        {
            "metrica": "Leituras com umidade em 10,0%",
            "valor": str(int(df["umidade"].eq(10.0).sum())),
            "observacao": (
                "Maior sequência: "
                f"{_maior_sequencia(df['umidade'].eq(10.0))} leituras — "
                "possível limite do sensor."
            ),
        },
        {
            "metrica": "Leituras com temperatura em 45,0 °C",
            "valor": str(int(df["temperatura"].eq(45.0).sum())),
            "observacao": (
                "Maior sequência: "
                f"{_maior_sequencia(df['temperatura'].eq(45.0))} leituras — "
                "pico curto no mesmo valor."
            ),
        },
        {
            "metrica": "Intervalo entre leituras",
            "valor": (
                f"{df['dt_s'].min():.3f} – {df['dt_s'].max():.3f} s"
            ).replace(".", ","),
            "observacao": (
                f"Mediana de {df['dt_s'].median():.3f} s.".replace(".", ",")
            ),
        },
        {
            "metrica": "Transições do cooler",
            "valor": str(int(df["cooler"].ne(df["cooler"].shift()).sum() - 1)),
            "observacao": "Um único ciclo liga–desliga no período.",
        },
        {
            "metrica": "Período analisado",
            "valor": (
                f"{df['timestamp'].min():%d/%m/%Y %H:%M:%S} – "
                f"{df['timestamp'].max():%H:%M:%S}"
            ),
            "observacao": "Horários sem fuso, como registrados no banco.",
        },
    ]


def correlacoes(
    metodo: str = "pearson", df: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Matriz de correlação com rótulos legíveis."""
    df = carregar_leituras() if df is None else df
    colunas = list(VARIABLE_LABELS)
    dados = df[colunas].rename(columns=VARIABLE_LABELS)
    return dados.corr(method=metodo).round(3)


def segmentos_estado(
    df: pd.DataFrame, coluna: str
) -> list[dict[str, Any]]:
    """Trechos contínuos de estado para colorir a linha sem cortes."""
    if df.empty:
        return []

    ts = pd.to_datetime(df["timestamp"]).reset_index(drop=True)
    y = pd.to_numeric(df[coluna], errors="coerce").to_numpy(dtype=float)
    estado = pd.to_numeric(df["cooler"], errors="coerce").astype(int).to_numpy()

    mudancas = np.flatnonzero(estado[1:] != estado[:-1]) + 1
    inicios = np.r_[0, mudancas]
    fins = np.r_[mudancas - 1, len(df) - 1]

    segmentos: list[dict[str, Any]] = []
    for inicio, fim in zip(inicios, fins):
        if inicio == 0:
            x0 = ts.iloc[inicio]
            y0 = y[inicio]
        else:
            x0 = ts.iloc[inicio - 1] + (ts.iloc[inicio] - ts.iloc[inicio - 1]) / 2
            y0 = (y[inicio - 1] + y[inicio]) / 2

        if fim == len(df) - 1:
            x1 = ts.iloc[fim]
            y1 = y[fim]
        else:
            x1 = ts.iloc[fim] + (ts.iloc[fim + 1] - ts.iloc[fim]) / 2
            y1 = (y[fim] + y[fim + 1]) / 2

        x = [x0, *ts.iloc[inicio : fim + 1].tolist(), x1]
        valores = [y0, *y[inicio : fim + 1], y1]
        segmentos.append(
            {"x": x, "y": valores, "cooler": int(estado[inicio])}
        )
    return segmentos


def faixas_estado(df: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Faixas de fundo com as fronteiras entre estados."""
    if df.empty:
        return []

    ts = pd.to_datetime(df["timestamp"]).reset_index(drop=True)
    estado = pd.to_numeric(df["cooler"], errors="coerce").astype(int).to_numpy()
    mudancas = np.flatnonzero(estado[1:] != estado[:-1]) + 1
    inicios = np.r_[0, mudancas]
    fins = np.r_[mudancas - 1, len(df) - 1]

    faixas: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
    for inicio, fim in zip(inicios, fins):
        if inicio == 0:
            x0 = ts.iloc[inicio]
        else:
            x0 = ts.iloc[inicio - 1] + (ts.iloc[inicio] - ts.iloc[inicio - 1]) / 2

        if fim == len(df) - 1:
            x1 = ts.iloc[fim]
        else:
            x1 = ts.iloc[fim] + (ts.iloc[fim + 1] - ts.iloc[fim]) / 2

        faixas.append((x0, x1, int(estado[inicio])))
    return faixas


def taxas_suavizadas(df: pd.DataFrame, janela: int = 5) -> pd.DataFrame:
    """Média móvel das taxas de variação."""
    janela = max(1, int(janela))
    base = df[["timestamp", "taxa_temperatura_c_min", "taxa_umidade_pct_min"]].copy()
    base["taxa_temperatura"] = (
        base["taxa_temperatura_c_min"]
        .rolling(window=janela, center=True, min_periods=2)
        .mean()
    )
    base["taxa_umidade"] = (
        base["taxa_umidade_pct_min"]
        .rolling(window=janela, center=True, min_periods=2)
        .mean()
    )
    return base
