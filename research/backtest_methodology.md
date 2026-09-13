# backtest_methodology.md — BTC Dynamic DCA

## 1. Pergunta que o backtest responde

Usando **apenas informação disponível naquele momento**, é possível alocar uma
parcela maior do **mesmo capital** em períodos em que o Bitcoin estava
relativamente barato e, com isso, acumular mais BTC no longo prazo?

A pergunta não é se o modelo enriquece; é se ele aloca melhor. Por isso o
comparativo central não é contra o DCA de 100/dia, e sim contra o **Cenário C**,
um DCA constante que gasta exatamente o mesmo dinheiro total do modelo dinâmico.

## 2. Preço utilizado

**OHLC4 = (Open + High + Low + Close)/4**, calculado a partir dos candles de 1
minuto da Bitstamp no par BTC/USD (par em dólar real, não USDT). Uma única fonte
de preço em todos os cenários e em todas as variantes testadas; nenhum backtest
mistura fontes. O VWAP diário também foi calculado e está disponível em
`data/btc_daily_bitstamp.csv`, mas o OHLC4 foi adotado por estar definido em
100% dos dias.

O preço da Coin Metrics (`cm_price`) existe no painel apenas para auditoria e
**nunca executa uma compra**.

## 3. Prevenção de look-ahead

Regra dura: uma informação só pode alterar o aporte **depois** de estar
disponível ao investidor.

- **Indicadores de preço** (Mayer, MM200D, MM200W, RSI semanal): defasagem de
  **1 dia**. O sinal calculado com o fechamento do dia D altera a compra do dia D+1.
- **Indicadores on-chain** (MVRV, Realized Price, NUPL, MVRV Z, Hash Ribbons):
  defasagem de **2 dias**, para absorver o atraso de publicação do feed da Coin
  Metrics. É deliberadamente conservador.
- **RSI semanal**: apenas semanas **encerradas** (domingo UTC). O valor de uma
  semana em curso nunca é usado.
- **Médias móveis**: somente preços até o dia do cálculo; `min_periods` igual à
  janela completa, sem preenchimento parcial.
- **Percentis históricos**: janela **expanding**, com no mínimo 365 observações
  anteriores. O percentil de hoje compara-se apenas ao passado.
- **MVRV Z-Score**: desvio-padrão **expanding** do market cap. Este ponto merece
  destaque: o MVRV Z-Score publicado pela maioria das fontes usa o desvio-padrão
  de toda a série histórica, o que significa que o valor mostrado para 2015 já
  embute o que aconteceu em 2021. Isso é look-ahead e foi eliminado aqui.
- **Otimização**: no walk-forward, os thresholds de cada janela são escolhidos
  usando somente dados anteriores à data de decisão.

## 4. Regras de execução

- Compra **todos os dias do calendário**, sem exceção, nas três estratégias.
- Aporte-base de 100 unidades monetárias por dia (escalável linearmente para
  qualquer valor; nenhum resultado relativo depende do valor-base).
- Cenário A: 100/dia fixo.
- Cenário B: 100 × multiplicador do modelo.
- Cenário C: `capital total de B ÷ número de dias`, constante. Calculado *ex post*
  apenas para definir o controle — é um benchmark de comparação, não uma
  estratégia implementável em tempo real. Isso é uma limitação assumida e é o
  desenho pedido no item 10 do briefing.
- Sem rebalanceamento, sem venda, sem alavancagem, sem timing de saída.

## 5. Métrica principal e sua identidade algébrica

A métrica central é a **BTC Efficiency**: BTC acumulado por B dividido pelo BTC
acumulado por C. Como C gasta o mesmo capital por construção, vale exatamente

```
Eficiência  =  E_w[1/p] / E[1/p]
```

onde `w` são os multiplicadores e `p` o preço diário. Em palavras: a estratégia
só vence se concentrar peso em dias que compram mais BTC por dólar. Essa
identidade foi verificada numericamente contra o motor completo (concordância até
a 8ª casa decimal) e é o que permite avaliar milhares de variantes rapidamente.

## 6. A armadilha metodológica central deste estudo

Numa série com crescimento exponencial, `E[1/p]` é dominado pelos dias mais
antigos da janela. Na janela 2013–2020, **64,9% de todo o "BTC por dólar"
disponível está concentrado apenas em 2013** (preço médio de US$187). Como o MVRV
nunca esteve abaixo de 1 em 2013, nenhum indicador de valuation poderia vencer
essa janela — e de fato todos apresentam lift abaixo de 1,0 nela.

Consequência: **medir a estratégia numa única janela de 14 anos mede sobretudo o
quão cedo ela concentra capital, não a habilidade do sinal.** Duas correções
foram adotadas:

1. **Janelas móveis** de 3, 4 e 5 anos (horizonte realista de um investidor),
   uma a cada 30 dias desde 2013. Reporta-se a distribuição completa: mediana,
   taxa de vitória, percentil 5 e pior janela.
2. **Teste de permutação circular dentro de cada janela**: o mesmo padrão de
   pesos é deslocado circularmente dentro da própria janela e a eficiência real é
   posicionada nessa distribuição nula. Rank próximo de 1,0 significa que o sinal
   está alinhado a dias baratos, e não meramente concentrado no início.

## 7. Custos

Backtest principal sem custos. Sensibilidade rodada a 0,05%, 0,10%, 0,25% e 0,50%
por compra, com premissa idêntica nas três estratégias. Resultado: como o custo é
proporcional ao valor comprado e as três estratégias compram todo dia, a
**eficiência relativa é matematicamente invariante ao custo** — apenas o nível
absoluto de BTC cai (0,50% de taxa custa 0,50% do BTC). Spread não foi modelado
por ausência de dados de book; para compras diárias de varejo em BTC/USD o
spread é de ordem inferior à taxa e afetaria as três estratégias igualmente.

## 8. Limitações assumidas

- **SOPR ausente.** Nenhuma fonte pública gratuita o publica. O modelo foi
  construído sem ele; a arquitetura permite acrescentá-lo depois.
- **O Cenário C é ex post.** Ninguém conhece o capital total futuro no dia 1. É o
  controle correto para isolar alocação de volume de capital, mas não é uma
  estratégia rival implementável.
- **MVRV tem revisões.** A Coin Metrics pode revisar a série; o backtest usa a
  versão corrente, não a que estava publicada em cada data histórica. Isso é um
  look-ahead residual impossível de eliminar sem um arquivo point-in-time do
  provedor. A defasagem de 2 dias mitiga, mas não elimina.
- **Um único ativo, uma única história.** O Bitcoin tem três ciclos completos
  observáveis. Qualquer conclusão sobre "ciclos" repousa sobre uma amostra de
  três. Nenhum teste estatístico corrige isso.
- **Sobrevivência do ativo.** O estudo condiciona-se ao fato de o Bitcoin ter
  sobrevivido e valorizado. Uma estratégia que compra mais na queda é, por
  construção, mais exposta ao cenário em que o ativo não se recupera.
- **Capital não alocado não rende.** O modelo assume que o dinheiro extra dos
  meses de multiplicador alto estava disponível e parado. Se estivesse rendendo
  CDI, o custo de oportunidade não está contabilizado.

## 9. Critério de escolha da estratégia vencedora

Na ordem do item 33 do briefing: (1) maior BTC acumulado com capital equivalente,
medido pela mediana das janelas móveis; (2) menor preço médio; (3) consistência
entre ciclos, medida pela taxa de janelas vencedoras e pela pior janela;
(4) desempenho fora da amostra no walk-forward; (5) estabilidade dos parâmetros
sob perturbação; (6) simplicidade; (7) menor necessidade de capital extraordinário.

## 10. Reprodução

```bash
python3 src/download_data.py        # busca as fontes públicas no GitHub
python3 src/build_price.py          # agrega 7,9M candles de 1 min em OHLC diário
python3 src/calculate_indicators.py # monta o painel mestre point-in-time
python3 src/final_run.py            # tabela principal + backtest_results.csv
python3 src/single_indicators.py    # lift marginal por indicador
python3 src/optimize.py             # grid de thresholds e multiplicadores
python3 src/validate.py             # walk-forward fora da amostra
```
