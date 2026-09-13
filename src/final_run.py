import sys; sys.path.insert(0,'src')
import numpy as np, pandas as pd, backtest as bt, final_model as fm, analyze as an
P, S = an.PANEL, an.SIG

score = fm.opportunity_score(S['mvrv'])
mult  = fm.multiplier(score, 'agressivo')
st    = fm.state(score)

def table(start, label):
    d, m, out = bt.run(P, mult, start=start)
    r, s, dist = bt.metrics(d, out, m)
    print('\n'+'='*104)
    print(f'{label}  |  {d.index.min().date()} -> {d.index.max().date()}  ({s["days"]} dias)  preco final US$ {s["final_price"]:,.0f}')
    print('='*104)
    hdr = f"{'Metrica':<26}{'A - DCA 100/dia':>22}{'B - DCA dinamico':>22}{'C - uniforme mesmo cap':>24}"
    print(hdr); print('-'*104)
    fmt = [('Capital investido','capital','{:,.0f}'),('BTC acumulado','btc','{:.6f}'),
           ('Preco medio','avg_price','{:,.0f}'),('Valor final','final_value','{:,.0f}'),
           ('Lucro','profit','{:,.0f}')]
    for nm,k,f in fmt:
        print(f"{nm:<26}"+''.join(f"{f.format(r.loc[c,k]):>22}" if c!='C_equal_capital' else f"{f.format(r.loc[c,k]):>24}"
              for c in ['A_fixed','B_dynamic','C_equal_capital']))
    print(f"{'ROI':<26}"+''.join(f"{r.loc[c,'roi']*100:>21.1f}%" if c!='C_equal_capital' else f"{r.loc[c,'roi']*100:>23.1f}%"
          for c in ['A_fixed','B_dynamic','C_equal_capital']))
    print(f"{'Max drawdown':<26}"+''.join(f"{r.loc[c,'max_dd']*100:>21.1f}%" if c!='C_equal_capital' else f"{r.loc[c,'max_dd']*100:>23.1f}%"
          for c in ['A_fixed','B_dynamic','C_equal_capital']))
    print(f"{'Maior aporte diario':<26}"+''.join(f"{r.loc[c,'max_daily']:>22,.0f}" if c!='C_equal_capital' else f"{r.loc[c,'max_daily']:>24,.0f}"
          for c in ['A_fixed','B_dynamic','C_equal_capital']))
    print('-'*104)
    print(f"{'BTC adicional vs C':<26}{'—':>22}{s['extra_btc_pct']:>21.2f}%{'—':>24}")
    print(f"{'Melhora do preco medio':<26}{'—':>22}{s['avg_cost_improvement']*100:>21.2f}%{'—':>24}")
    print(f"{'BTC adicional vs A':<26}{'—':>22}{s['btc_vs_A_pct']:>21.2f}%{'—':>24}")
    print(f"\nDistribuicao dos multiplicadores (% dos dias): "+
          ', '.join(f'{k:g}x: {v:.1f}%' for k,v in dist.items()))
    print(f"Capital exigido nos piores 30 dias: {s['worst30_capital']:,.0f}  |  90 dias: {s['worst90_capital']:,.0f}"
          f"   (DCA fixo: 3.000 / 9.000)")
    return r, s, dist

table('2021-01-01','BACKTEST PRINCIPAL (obrigatorio, item 8)')
table('2013-01-01','HISTORICO COMPLETO')
table('2013-01-01','TREINO (pre-2021)') if False else None
d,m,o = bt.run(P, mult, start='2013-01-01', end='2020-12-31'); r,s,_=bt.metrics(d,o,m)
print(f"\nJanela de treino 2013-2020: eficiencia B/C = {s['btc_efficiency']:.4f} ({s['extra_btc_pct']:+.2f}% BTC) "
      f"— NEGATIVA, ver relatorio secao 'o que nao funcionou'")

# ---------------- ENTREGAVEL 4: backtest_results.csv
d, m, out = bt.run(P, mult, start='2013-01-01')
res = pd.DataFrame({
 'date': d.index.date, 'btc_price': d['ohlc4'], 'btc_close': d['close'],
 'mvrv': d['mvrv'], 'mvrv_zscore': d['mvrv_zscore'], 'mayer_multiple': d['mayer'],
 'rsi_weekly': d['rsi_weekly'], 'ma200d': d['ma200d'], 'ma200w': d['ma200w'],
 'realized_price': d['realized_price'], 'nupl': d['nupl'], 'sopr': np.nan,
 'hash_ribbon': d['hash_ribbon'],
 'opportunity_score': score.reindex(d.index), 'state': st.reindex(d.index),
 'multiplier': m,
 'dynamic_investment': out['B_dynamic']['invested'],
 'dynamic_btc_bought': out['B_dynamic']['btc'],
 'dynamic_btc_total': out['B_dynamic']['cum_btc'],
 'normal_dca_btc_total': out['A_fixed']['cum_btc'],
 'equal_capital_dca_btc_total': out['C_equal_capital']['cum_btc'],
 'dynamic_capital_total': out['B_dynamic']['cum_inv'],
})
res.to_csv('out/backtest_results.csv', index=False)
print(f"\nbacktest_results.csv gravado: {len(res)} linhas, {res.shape[1]} colunas")
print(f"SINAL DE HOJE ({d.index[-1].date()}): MVRV={d['mvrv'].iloc[-1]:.4f} score={score.iloc[-1]:.1f} "
      f"estado={st.iloc[-1]} multiplicador={m.iloc[-1]:g}x")
