"""Suite de testes do alerta de orçamento de nuvem (finops-alerta-orcamento)."""

from pathlib import Path

import pytest

from finops_alerta_orcamento import (
    Orcamento,
    avaliar,
    carregar_orcamento,
    disparar_alerta,
    ler_fatura,
)


@pytest.fixture
def fatura_csv(tmp_path: Path) -> Path:
    """Fatura CSV com total 165,80 (EC2 120,50 + S3 45,30 + RDS 60,00)."""
    caminho = tmp_path / "fatura.csv"
    caminho.write_text(
        "conta,periodo,servico,valor\n"
        "123456789012,2026-09,EC2,120.50\n"
        "123456789012,2026-09,S3,45.30\n"
        "123456789012,2026-09,RDS,60.00\n",
        encoding="utf-8",
    )
    return caminho


@pytest.fixture
def fatura_json(tmp_path: Path) -> Path:
    """Fatura JSON equivalente à fatura CSV (total 165,80)."""
    caminho = tmp_path / "fatura.json"
    caminho.write_text(
        '{"conta": "123456789012", "periodo": "2026-09", '
        '"itens": [{"servico": "EC2", "valor": 120.50}, '
        '{"servico": "S3", "valor": 45.30}, '
        '{"servico": "RDS", "valor": 60.00}]}',
        encoding="utf-8",
    )
    return caminho


@pytest.fixture
def orcamento_json(tmp_path: Path) -> Path:
    """Orçamento: limite 200,00 e alerta a partir de 80%."""
    caminho = tmp_path / "orcamento.json"
    caminho.write_text(
        '{"conta": "123456789012", "periodo": "2026-09", '
        '"limite_total": 200.0, "limite_percentual_alerta": 80}',
        encoding="utf-8",
    )
    return caminho


# --- leitura de fatura -----------------------------------------------------

def test_ler_fatura_csv_total(fatura_csv: Path) -> None:
    fatura = ler_fatura(fatura_csv)
    assert fatura.conta == "123456789012"
    assert fatura.periodo == "2026-09"
    assert len(fatura.itens) == 3
    assert fatura.total == pytest.approx(225.80)


def test_ler_fatura_json_total(fatura_json: Path) -> None:
    fatura = ler_fatura(fatura_json)
    assert fatura.total == pytest.approx(225.80)


def test_ler_fatura_arquivo_inexistente(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ler_fatura(tmp_path / "nao_existe.csv")


def test_ler_fatura_formato_nao_suportado(tmp_path: Path) -> None:
    caminho = tmp_path / "fatura.txt"
    caminho.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="Formato não suportado"):
        ler_fatura(caminho)


# --- leitura de orçamento --------------------------------------------------

def test_carregar_orcamento(orcamento_json: Path) -> None:
    orcamento = carregar_orcamento(orcamento_json)
    assert orcamento.conta == "123456789012"
    assert orcamento.periodo == "2026-09"
    assert orcamento.limite_total == pytest.approx(200.0)
    assert orcamento.limite_percentual_alerta == pytest.approx(80.0)


def test_carregar_orcamento_arquivo_inexistente(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        carregar_orcamento(tmp_path / "orcamento.json")


# --- avaliação: alerta dispara --------------------------------------------

def test_avaliar_alerta_disparado(fatura_csv: Path, orcamento_json: Path) -> None:
    # 225,80 / 200,00 = 112,9% >= 80% → dispara
    fatura = ler_fatura(fatura_csv)
    orcamento = carregar_orcamento(orcamento_json)
    alerta = avaliar(fatura, orcamento)

    assert alerta.disparado is True
    assert alerta.percentual_uso == pytest.approx(112.9)
    assert alerta.total_fatura == pytest.approx(225.80)
    assert "ALERTA" in alerta.mensagem


def test_avaliar_mesmo_resultado_csv_json(
    fatura_csv: Path, fatura_json: Path, orcamento_json: Path
) -> None:
    orcamento = carregar_orcamento(orcamento_json)
    alerta_csv = avaliar(ler_fatura(fatura_csv), orcamento)
    alerta_json = avaliar(ler_fatura(fatura_json), orcamento)
    assert alerta_csv.disparado == alerta_json.disparado
    assert alerta_csv.percentual_uso == pytest.approx(alerta_json.percentual_uso)


def test_avaliar_limite_exato_dispara(fatura_csv: Path, tmp_path: Path) -> None:
    # 165,80 / 207,25 = 80,0% → dispara (>=)
    orcamento_caminho = tmp_path / "orcamento.json"
    orcamento_caminho.write_text(
        '{"conta": "123456789012", "periodo": "2026-09", '
        '"limite_total": 282.25, "limite_percentual_alerta": 80}',
        encoding="utf-8",
    )
    fatura = ler_fatura(fatura_csv)
    orcamento = carregar_orcamento(orcamento_caminho)
    alerta = avaliar(fatura, orcamento)

    assert alerta.disparado is True
    assert alerta.percentual_uso == pytest.approx(80.0)


# --- avaliação: alerta não dispara ----------------------------------------

def test_avaliar_alerta_nao_disparado(fatura_csv: Path, tmp_path: Path) -> None:
    # 225,80 / 1000,00 = 22,58% < 80% → não dispara
    orcamento_caminho = tmp_path / "orcamento.json"
    orcamento_caminho.write_text(
        '{"conta": "123456789012", "periodo": "2026-09", '
        '"limite_total": 1000.0, "limite_percentual_alerta": 80}',
        encoding="utf-8",
    )
    fatura = ler_fatura(fatura_csv)
    orcamento = carregar_orcamento(orcamento_caminho)
    alerta = avaliar(fatura, orcamento)

    assert alerta.disparado is False
    assert alerta.percentual_uso == pytest.approx(22.58)
    assert "OK" in alerta.mensagem


# --- validações de negócio ------------------------------------------------

def test_avaliar_conta_diferente_erro(fatura_csv: Path, tmp_path: Path) -> None:
    orcamento_caminho = tmp_path / "orcamento.json"
    orcamento_caminho.write_text(
        '{"conta": "999999999999", "periodo": "2026-09", '
        '"limite_total": 200.0, "limite_percentual_alerta": 80}',
        encoding="utf-8",
    )
    fatura = ler_fatura(fatura_csv)
    orcamento = carregar_orcamento(orcamento_caminho)
    with pytest.raises(ValueError, match="Conta da fatura"):
        avaliar(fatura, orcamento)


def test_avaliar_periodo_diferente_erro(fatura_csv: Path, tmp_path: Path) -> None:
    orcamento_caminho = tmp_path / "orcamento.json"
    orcamento_caminho.write_text(
        '{"conta": "123456789012", "periodo": "2026-10", '
        '"limite_total": 200.0, "limite_percentual_alerta": 80}',
        encoding="utf-8",
    )
    fatura = ler_fatura(fatura_csv)
    orcamento = carregar_orcamento(orcamento_caminho)
    with pytest.raises(ValueError, match="Período da fatura"):
        avaliar(fatura, orcamento)


def test_orcamento_limite_zero_erro() -> None:
    orcamento = Orcamento(
        conta="123456789012",
        periodo="2026-09",
        limite_total=0.0,
        limite_percentual_alerta=80,
    )
    with pytest.raises(ValueError, match="limite_total"):
        orcamento.percentual_uso(100.0)


# --- saída do alerta ------------------------------------------------------

def test_disparar_alerta_imprime_mensagem(
    capsys: pytest.CaptureFixture, fatura_csv: Path, orcamento_json: Path
) -> None:
    fatura = ler_fatura(fatura_csv)
    orcamento = carregar_orcamento(orcamento_json)
    alerta = avaliar(fatura, orcamento)
    disparar_alerta(alerta)

    capturado = capsys.readouterr()
    assert alerta.mensagem in capturado.out
