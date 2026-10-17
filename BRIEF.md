# BRIEF — finops-alerta-orcamento

## Projeto
**Nome:** finops-alerta-orcamento  
**Área:** DevOps/Cloud  
**Stack:** Python (sem dependências externas); CLI AWS/Azure como referência de operação, mas execução 100% local sobre arquivos — sem credenciais reais de nuvem.

## Escopo MVP
Alerta de orçamento de nuvem: lê uma fatura simulada (CSV/JSON local), compara o total com um orçamento e dispara um alerta quando o uso atinge/excede um limite percentual.

## Critérios de aceitação (todos verificados)
- Alerta dispara quando o gasto excede o limite (saída 1); não dispara quando dentro (saída 0).
- Suíte de testes passa.
- README bilíngue PT-BR + EN completo.

## Arquivos criados
| Caminho | Conteúdo |
|---|---|
| `pyproject.toml` | Metadados, entry point `finops-alerta`, config ruff |
| `src/finops_alerta_orcamento/__init__.py` | Pacote, exports, versão |
| `src/finops_alerta_orcamento/models.py` | Dataclasses: FaturaItem, Fatura, Orcamento, Alerta |
| `src/finops_alerta_orcamento/alerta.py` | Leitura CSV/JSON, carga de orçamento, avaliação, emissão de alerta |
| `src/finops_alerta_orcamento/cli.py` | Interface de linha de comando |
| `data/fatura_simulada.csv` | Fatura simulada CSV (3 itens, total R$ 225,80) |
| `data/fatura_simulada.json` | Fatura simulada JSON (mesma fatura) |
| `data/orcamento.json` | Orçamento: limite R$ 200,00, alerta a 80% |
| `tests/test_alerta.py` | 14 testes pytest |
| `README.md` | Documentação bilíngue PT-BR + EN |
| `BRIEF.md` | Este arquivo |

## Como verificar

### 1. Lint
```bash
# Windows (PowerShell)
python -m ruff check .
# Unix
python -m ruff check .
```
Resultado esperado: `All checks passed!`

### 2. Testes
```bash
# Windows (PowerShell)
$env:PYTHONPATH="src"; python -m pytest -q
# Unix
export PYTHONPATH=src; python -m pytest -q
```
Resultado esperado: `14 passed in 0.15s`

### 3. Alerta dispara (CLI)
```bash
# Windows (PowerShell)
$env:PYTHONPATH="src"; python -m finops_alerta_orcamento.cli data\fatura_simulada.csv data\orcamento.json
# Unix
export PYTHONPATH=src; python -m finops_alerta_orcamento.cli data/fatura_simulada.csv data/orcamento.json
```
Saída esperada:
```
ALERTA: fatura 123456789012/2026-09 total R$ 225.80 excede 80% do orçamento R$ 200.00 (uso 112.9%)
```
Código de saída: 1 (alerta disparado).

## Caminhos
- README: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\finops-alerta-orcamento\README.md`
- BRIEF: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\finops-alerta-orcamento\BRIEF.md`
- Raiz do projeto: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\finops-alerta-orcamento\`
