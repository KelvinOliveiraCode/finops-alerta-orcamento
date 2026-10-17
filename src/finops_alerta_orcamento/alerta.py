"""Lógica de negócio: ler fatura, comparar orçamento, disparar alerta."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .models import Alerta, Fatura, FaturaItem, Orcamento


def ler_fatura_csv(caminho: Path) -> Fatura:
    """Lê uma fatura simulada de um arquivo CSV local.

    Espera colunas: conta, periodo, servico, valor.
    """
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de fatura não encontrado: {caminho}")

    conta: str | None = None
    periodo: str | None = None
    itens: List[FaturaItem] = []

    with caminho.open("r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        obrigatorias = {"conta", "periodo", "servico", "valor"}
        if (
            leitor.fieldnames is None
            or not obrigatorias.issubset(set(leitor.fieldnames))
        ):
            raise ValueError(
                f"CSV de fatura deve conter colunas {sorted(obrigatorias)}: {caminho}"
            )
        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                valor = float(linha["valor"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Valor inválido na linha {numero_linha} de {caminho}: {linha['valor']!r}"
                ) from exc
            conta = linha["conta"]
            periodo = linha["periodo"]
            itens.append(FaturaItem(servico=linha["servico"], valor=valor))

    if conta is None or periodo is None or not itens:
        raise ValueError(f"CSV de fatura está vazio ou sem dados: {caminho}")

    return Fatura(conta=conta, periodo=periodo, itens=itens)


def ler_fatura_json(caminho: Path) -> Fatura:
    """Lê uma fatura simulada de um arquivo JSON local.

    Estrutura esperada:
        {"conta": "...", "periodo": "...", "itens": [{"servico": "...", "valor": 1.0}, ...]}
    """
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de fatura não encontrado: {caminho}")

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON de fatura inválido: {caminho}: {exc}") from exc

    try:
        conta = str(dados["conta"])
        periodo = str(dados["periodo"])
        itens_raw = dados["itens"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            f"JSON de fatura faltando campos obrigatórios: {caminho}: {exc}"
        ) from exc

    itens: List[FaturaItem] = []
    for indice, item in enumerate(itens_raw):
        try:
            itens.append(
                FaturaItem(servico=str(item["servico"]), valor=float(item["valor"]))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Item inválido na posição {indice} do JSON de fatura: {caminho}: {exc}"
            ) from exc

    if not itens:
        raise ValueError(f"JSON de fatura não contém itens: {caminho}")

    return Fatura(conta=conta, periodo=periodo, itens=itens)


def ler_fatura(caminho: Path) -> Fatura:
    """Lê uma fatura simulada detectando o formato pela extensão (.csv ou .json)."""
    sufixo = caminho.suffix.lower()
    if sufixo == ".csv":
        return ler_fatura_csv(caminho)
    if sufixo == ".json":
        return ler_fatura_json(caminho)
    raise ValueError(
        f"Formato não suportado para fatura (use .csv ou .json): {caminho}"
    )


def carregar_orcamento(caminho: Path) -> Orcamento:
    """Carrega o orçamento de um arquivo JSON local.

    Estrutura esperada:
        {"conta": "...", "periodo": "...", "limite_total": 100.0, "limite_percentual_alerta": 80}
    """
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de orçamento não encontrado: {caminho}")

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON de orçamento inválido: {caminho}: {exc}") from exc

    try:
        return Orcamento(
            conta=str(dados["conta"]),
            periodo=str(dados["periodo"]),
            limite_total=float(dados["limite_total"]),
            limite_percentual_alerta=float(dados["limite_percentual_alerta"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"JSON de orçamento inválido: {caminho}: {exc}") from exc


def avaliar(fatura: Fatura, orcamento: Orcamento) -> Alerta:
    """Compara a fatura contra o orçamento e retorna o alerta.

    O alerta dispara quando o percentual de uso atinge ou excede
    limite_percentual_alerta. Lança ValueError se conta/período não conferem.
    """
    if fatura.conta != orcamento.conta:
        raise ValueError(
            f"Conta da fatura ({fatura.conta}) difere da conta do orçamento ({orcamento.conta})"
        )
    if fatura.periodo != orcamento.periodo:
        mensagem_erro = (
            f"Período da fatura ({fatura.periodo}) difere do período do orçamento "
            f"({orcamento.periodo})"
        )
        raise ValueError(mensagem_erro)

    total_fatura = fatura.total
    percentual_uso = orcamento.percentual_uso(total_fatura)
    disparado = percentual_uso >= orcamento.limite_percentual_alerta

    if disparado:
        mensagem = (
            f"ALERTA: fatura {fatura.conta}/{fatura.periodo} total R$ {total_fatura:.2f} "
            f"excede {orcamento.limite_percentual_alerta:.0f}% do orçamento "
            f"R$ {orcamento.limite_total:.2f} (uso {percentual_uso:.1f}%)"
        )
    else:
        mensagem = (
            f"OK: fatura {fatura.conta}/{fatura.periodo} total R$ {total_fatura:.2f} "
            f"dentro do orçamento R$ {orcamento.limite_total:.2f} "
            f"(uso {percentual_uso:.1f}%, limite {orcamento.limite_percentual_alerta:.0f}%)"
        )

    return Alerta(
        disparado=disparado,
        conta=fatura.conta,
        periodo=fatura.periodo,
        total_fatura=total_fatura,
        limite_total=orcamento.limite_total,
        percentual_uso=percentual_uso,
        limite_percentual_alerta=orcamento.limite_percentual_alerta,
        mensagem=mensagem,
    )


def disparar_alerta(alerta: Alerta) -> None:
    """Emite o alerta no stdout. Não usa credenciais reais de nuvem."""
    print(alerta.mensagem)
