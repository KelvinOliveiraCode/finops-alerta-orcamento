"""Interface de linha de comando do alerta de orçamento de nuvem."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .alerta import avaliar, carregar_orcamento, disparar_alerta, ler_fatura


def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="finops-alerta",
        description="Lê fatura simulada local, compara contra orçamento e dispara alerta.",
    )
    parser.add_argument(
        "fatura",
        type=Path,
        help="Caminho do arquivo de fatura simulada (.csv ou .json).",
    )
    parser.add_argument(
        "orcamento",
        type=Path,
        help="Caminho do arquivo de orçamento (.json).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI. Retorna 1 se o alerta disparou, 0 caso contrário."""
    parser = build_parser()
    args = parser.parse_args(argv)

    fatura = ler_fatura(args.fatura)
    orcamento = carregar_orcamento(args.orcamento)
    alerta = avaliar(fatura, orcamento)
    disparar_alerta(alerta)

    return 1 if alerta.disparado else 0


if __name__ == "__main__":
    sys.exit(main())
