# finops-alerta-orcamento

Alerta de orçamento de nuvem (MVP). Lê uma fatura simulada local (CSV ou JSON), compara com um orçamento e imprime um alerta quando o gasto excede o limite percentual. Sem credenciais reais de nuvem: tudo roda sobre arquivos locais.

-- PT-BR --

## O que faz

Lê uma fatura simulada (CSV/JSON) da pasta `data/`, soma o total dos itens, compara com o orçamento de `data/orcamento.json` e imprime uma mensagem no console quando o uso atinge ou excede o percentual de alerta (padrão: 80%).

## Como usar

Requisitos: Python 3.10+.

```bash
cd finops-alerta-orcamento
set PYTHONPATH=src
python -m finops_alerta_orcamento.cli data\fatura_simulada.csv data\orcamento.json
```

Saída esperada (a fatura de exemplo totaliza R$ 225,80 contra orçamento de R$ 200,00 = 112,9%):

```
ALERTA: fatura 123456789012/2026-09 total R$ 225.80 excede 80% do orçamento R$ 200.00 (uso 112.9%)
```

O programa retorna código de saída 1 quando o alerta dispara e 0 quando não dispara.

## Formato dos arquivos

Fatura CSV (colunas: conta, periodo, servico, valor):

```
conta,periodo,servico,valor
123456789012,2026-09,EC2,120.50
123456789012,2026-09,S3,45.30
123456789012,2026-09,RDS,60.00
```

Fatura JSON:

```json
{
  "conta": "123456789012",
  "periodo": "2026-09",
  "itens": [
    {"servico": "EC2", "valor": 120.50},
    {"servico": "S3", "valor": 45.30},
    {"servico": "RDS", "valor": 60.00}
  ]
}
```

Orçamento JSON:

```json
{
  "conta": "123456789012",
  "periodo": "2026-09",
  "limite_total": 200.00,
  "limite_percentual_alerta": 80
}
```

## Testes

```bash
set PYTHONPATH=src
python -m pytest -q
```

Resultado: 14 testes passam.

## Licença

MIT.

## Autor

Kelvin Oliveira

-- EN --

## What it does

Reads a simulated bill (CSV/JSON) from `data/`, sums the item totals, compares against the budget in `data/orcamento.json`, and prints a message to the console when usage reaches or exceeds the alert percentage (default: 80%). No real cloud credentials: everything runs on local files.

## How to use

Requirements: Python 3.10+.

```bash
cd finops-alerta-orcamento
export PYTHONPATH=src
python -m finops_alerta_orcamento.cli data/fatura_simulada.csv data/orcamento.json
```

Expected output (the sample bill totals R$ 225.80 vs budget R$ 200.00 = 112.9%):

```
ALERTA: fatura 123456789012/2026-09 total R$ 225.80 excede 80% do orçamento R$ 200.00 (uso 112.9%)
```

The program returns exit code 1 when the alert fires and 0 when it does not.

## File formats

Simulated bill CSV (columns: account, period, service, value):

```
conta,periodo,servico,valor
123456789012,2026-09,EC2,120.50
123456789012,2026-09,S3,45.30
123456789012,2026-09,RDS,60.00
```

Simulated bill JSON:

```json
{
  "conta": "123456789012",
  "periodo": "2026-09",
  "itens": [
    {"servico": "EC2", "valor": 120.50},
    {"servico": "S3", "valor": 45.30},
    {"servico": "RDS", "valor": 60.00}
  ]
}
```

Budget JSON:

```json
{
  "conta": "123456789012",
  "periodo": "2026-09",
  "limite_total": 200.00,
  "limite_percentual_alerta": 80
}
```

## Tests

```bash
export PYTHONPATH=src
python -m pytest -q
```

Result: 14 tests pass.

## License

MIT.

## Author

Kelvin Oliveira
