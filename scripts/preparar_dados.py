#!/usr/bin/env python3
"""Gera o snapshot de dados usado pelo dashboard.

O dashboard é publicado sem acesso ao PostgreSQL institucional. Este script
converte o CSV produzido por ``analise_leituras.py`` (separador ``;``, decimal
``,``) em um snapshot normalizado (UTF-8, separador ``,``, decimal ``.``) que é
versionado em ``dashboard/data/leituras.csv``.

Uso:
    python scripts/preparar_dados.py
    python scripts/preparar_dados.py --origem /caminho/leituras_tratadas.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
ORIGEM_PADRAO = BASE_DIR / "reports" / "tabelas" / "leituras_tratadas.csv"
DESTINO_PADRAO = BASE_DIR / "dashboard" / "data" / "leituras.csv"

COLUNAS = [
    "id",
    "timestamp",
    "temperatura",
    "umidade",
    "cooler",
    "dt_s",
    "tempo_s",
    "taxa_temperatura_c_min",
    "taxa_umidade_pct_min",
]


def preparar(origem: Path, destino: Path) -> pd.DataFrame:
    if not origem.exists():
        raise FileNotFoundError(
            f"Arquivo de origem não encontrado: {origem}. "
            "Execute 'python analise_leituras.py' antes."
        )

    df = pd.read_csv(
        origem,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        parse_dates=["timestamp"],
        usecols=COLUNAS,
    )
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["cooler"] = df["cooler"].astype(int)
    df["id"] = df["id"].astype(int)

    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        destino,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d %H:%M:%S.%f",
        float_format="%.6f",
    )
    return df


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origem", type=Path, default=ORIGEM_PADRAO)
    parser.add_argument("--destino", type=Path, default=DESTINO_PADRAO)
    args = parser.parse_args()

    df = preparar(args.origem, args.destino)
    print(f"{len(df)} leituras gravadas em {args.destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
