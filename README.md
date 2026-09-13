# BTC Dynamic DCA

Sistema quantitativo de aporte diario em Bitcoin com peso variavel. O painel e
estatico: um HTML e um arquivo de dados. Nao ha servidor, banco nem processo em
execucao.

- `site/` — o painel publicado (documento HTML completo). E isto que o GitHub Pages serve.
- `app/` — o mesmo painel como fragmento, para publicar como Artifact no Claude.
- `src/` — pipeline reproduzivel de dados, indicadores, backtest e otimizacao.
- `data/btc_daily_bitstamp.csv` — cache do OHLC diario. E o que deixa a atualizacao diaria leve.
- `out/` — `backtest_results.csv` e todas as tabelas da pesquisa.
- `research/` — relatorio, dicionario de dados e metodologia.

## Atualizar os dados

```bash
pip install -r requirements.txt
python src/update_daily.py      # ~5 MB de download, poucos segundos
```

Se o cache `data/btc_daily_bitstamp.csv` nao existir, rode uma vez:

```bash
python src/bootstrap.py         # ~143 MB, alguns minutos
```

No GitHub, o workflow `.github/workflows/daily.yml` faz isso sozinho todo dia.

## O modelo

Dois motores, com chave nas Configuracoes do painel:

1. **Escada de MVRV** (recomendada) — cortes 1,20 / 1,00 / 0,95 / 0,90 para
   multiplicadores 1,5x / 2x / 3x / 4x.
2. **Score composto** — MVRV (45), Preco/MM200W (30), RSI semanal (15),
   Mayer (10), com cortes 70 / 76 / 82 / 88.

Metodologia, validacao fora da amostra e o registro do que nao funcionou estao
em `research/research_report.md`.

Nada aqui e recomendacao de investimento.
