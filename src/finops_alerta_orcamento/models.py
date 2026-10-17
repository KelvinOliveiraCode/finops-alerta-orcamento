"""Modelos de domínio do alerta de orçamento de nuvem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class FaturaItem:
    """Um item de serviço na fatura simulada."""

    servico: str
    valor: float


@dataclass(frozen=True)
class Fatura:
    """Fatura simulada lida de um arquivo local (CSV ou JSON)."""

    conta: str
    periodo: str
    itens: List[FaturaItem]

    @property
    def total(self) -> float:
        """Soma dos valores de todos os itens da fatura."""
        return sum(item.valor for item in self.itens)


@dataclass(frozen=True)
class Orcamento:
    """Orçamento de referência usado para comparação."""

    conta: str
    periodo: str
    limite_total: float
    limite_percentual_alerta: float

    def percentual_uso(self, total_fatura: float) -> float:
        """Percentual do orçamento consumido pela fatura informada."""
        if self.limite_total <= 0:
            raise ValueError("limite_total do orçamento deve ser maior que zero")
        return (total_fatura / self.limite_total) * 100.0


@dataclass(frozen=True)
class Alerta:
    """Resultado da comparação entre fatura e orçamento."""

    disparado: bool
    conta: str
    periodo: str
    total_fatura: float
    limite_total: float
    percentual_uso: float
    limite_percentual_alerta: float
    mensagem: str
