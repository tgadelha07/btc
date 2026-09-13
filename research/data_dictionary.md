# data_dictionary.md — BTC Dynamic DCA

Gerado em 2026-09-13. Todas as séries abaixo existem em `data/master_panel.csv`
(5.369 linhas, 2012-01-01 a 2026-09-12) e alimentam `out/backtest_results.csv`.

## Restrição de ambiente que moldou a escolha de fontes

A política de rede deste ambiente nega conexão a praticamente todas as APIs de
cripto: `community-api.coinmetrics.io`, `api.binance.com`, `api.coingecko.com`,
`api.exchange.coinbase.com`, `api.blockchain.info`, `min-api.cryptocompare.com`,
`api.kraken.com`, `query1.finance.yahoo.com`, `huggingface.co`, `kaggle.com`,
`storage.googleapis.com` — todas respondem 403 no CONNECT. O GitHub é acessível.
Portanto cada fonte abaixo é obtida de um repositório público do GitHub, mas em
todos os casos o dado é o do **provedor original**, não uma re-derivação de
terceiros. Nenhum valor foi fabricado, interpolado ou extrapolado em nenhum ponto.

## Séries primárias

| Variável | Significado | Fonte | Frequência | Período disponível | Unidade | Transformação aplicada |
|---|---|---|---|---|---|---|
| `open` `high` `low` `close` | OHLC diário do par BTC/USD | Bitstamp, candles de 1 minuto, repositório `ff137/bitstamp-btcusd-minute-data` | diária (agregada de 1 min) | 2012-01-01 → 2026-09-12 | USD | agregação própria dos 1.440 candles de cada dia UTC: first/max/min/last |
| `volume` | Volume negociado no dia | idem | diária | idem | BTC | soma dos minutos |
| `vwap` | Preço médio ponderado por volume | idem | diária | idem | USD | Σ(close·vol)/Σvol sobre os minutos |
| `ohlc4` | **Preço de execução de todas as compras** | idem | diária | idem | USD | (O+H+L+C)/4 |
| `n` | Minutos observados no dia | idem | diária | idem | contagem | controle de integridade; dias com n<1400 descartados |
| `mvrv` | Market Value / Realized Value | Coin Metrics community (`CapMVRVCur`), espelho `akpasz/btc-data` | diária | 2010-07-18 → 2026-09-12 | razão | deslocamento de −1 dia para desfazer o shift do espelho e restaurar a convenção nativa da Coin Metrics |
| `market_cap` | Capitalização de mercado corrente | Coin Metrics (`CapMrktCurUSD`), mesmo espelho | diária | idem | USD | idem |
| `supply` | Oferta corrente de BTC | Coin Metrics (`SplyCur`) | diária | 2010-07-18 → 2026-09-12 | BTC | idem |
| `hashrate` | Hash rate médio da rede | Coin Metrics (`HashRate`) | diária | idem | hashes/s | idem |
| `cm_price` | Preço de referência da Coin Metrics | Coin Metrics (`PriceUSD`) | diária | idem | USD | usado só para auditoria, **nunca** para executar compras |

## Séries derivadas

| Variável | Definição | Observação |
|---|---|---|
| `realized_cap` | `market_cap / mvrv` | o tier community da Coin Metrics não publica `CapRealUSD`; esta é a identidade exata para recuperá-lo |
| `realized_price` | `realized_cap / supply` | preço médio de aquisição de toda a rede |
| `price_to_rp` | `close / realized_price` | correlação de Spearman 0,995 com `mvrv` — redundante |
| `nupl` | `1 − 1/mvrv` | **identidade algébrica**, não aproximação: NUPL = (MC−RC)/MC. Correlação 1,000 com `mvrv` |
| `mvrv_zscore` | `(market_cap − realized_cap) / std_expanding(market_cap)` | desvio-padrão **expanding**, nunca de amostra cheia. O Z-Score publicado na maioria das fontes usa o desvio de toda a série, o que embute look-ahead |
| `ma200d` | média móvel simples de 200 dias de `close` | — |
| `mayer` | `close / ma200d` | — |
| `ma200w` | média móvel simples de 1.400 dias de `close` | disponível só a partir de 2015-10-31 |
| `p_ma200w` | `close / ma200w` | — |
| `rsi_weekly` | RSI(14) de Wilder sobre fechamentos semanais (semana encerrada no domingo UTC) | só semanas **fechadas**; propagado para os dias seguintes |
| `hr_ma30`, `hr_ma60` | médias móveis de 30 e 60 dias do hash rate | — |
| `hash_ribbon` | 1 = capitulação de mineradores (MA30 < MA60); 2 = 30 dias após o cruzamento de recuperação; 0 = normal | metodologia Capriole |
| `pct_<x>` | percentil histórico **expanding** de `<x>` (mínimo 365 observações prévias) | fração dos dias anteriores com valor inferior ao de hoje; nunca usa o futuro |
| `opportunity_score` | função linear por partes de `mvrv` (ver `src/final_model.py`) | 0–100; os cortes 50/70/80/90 são exatamente MVRV 1,20/1,00/0,95/0,90 |

## Séries que NÃO foi possível obter

| Variável | Situação | Encaminhamento |
|---|---|---|
| `sopr` / `aSOPR` | **Indisponível.** Nenhuma fonte pública gratuita publica SOPR: o cálculo exige dados em nível de UTXO ou de entidades agrupadas. O repositório `akpasz/btc-data` documenta explicitamente essa lacuna e se recusa a aproximá-la, o que é a conduta correta. | Coluna presente e vazia em `backtest_results.csv`. O backtest seguiu sem ela (item 36). Se um dia houver acesso a Glassnode ou CryptoQuant pagos, basta preencher a coluna e repetir `src/optimize.py`. |
| `CapRealUSD` direto | Não publicado no tier community | Recuperado pela identidade `market_cap / mvrv` |
| Supply age bands (`SplyAct*`) | Não publicado no tier community | Não utilizados |

## Validação cruzada realizada

1. **Dois espelhos independentes da Coin Metrics**: `akpasz/btc-data` (diário) e
   `coinmetrics/data` (arquivo CSV, defasado desde 2026-05-24). Após desfazer o
   shift de +1 dia do primeiro, as séries coincidem em 4.161 dias sobrepostos com
   diferença máxima de **4,4×10⁻¹⁶** e correlação **1,00000000**. É a mesma série.
2. **Provedor independente**: o MVRV da CryptoQuant (via `ErcinDedeoglu/crypto-market-data`,
   2022-12 em diante) marca 1,4517 em 2026-09-11 contra 1,4519 da Coin Metrics — 0,01% de
   diferença, apesar de metodologias distintas.
3. **Integridade do preço**: 5.370 dias entre 2012-01-01 e 2026-09-13, **zero dias
   faltando** no calendário. Apenas 2 dias com menos de 1.440 minutos (o primeiro dia
   da série e o dia corrente, parcial — este foi descartado).
