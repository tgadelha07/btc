import sys; sys.path.insert(0,'src')
import numpy as np, pandas as pd, json, os
import backtest as bt, final_model as fm, analyze as an, rolling as rl
P,S = an.PANEL, an.SIG

SCORES = {'mvrv': fm.opportunity_score(S['mvrv']), 'composto': fm.composite_score(S)}
def jn(x):
    if x is None: return None
    try: x=float(x)
    except Exception: return None
    return None if (np.isnan(x) or np.isinf(x)) else round(x,6)

last = P.index[-1]
def ctx(col, val, cheap_col=None):
    s = P[col].dropna()
    if val is None or val!=val: return None
    d = dict(value=jn(val), pct=round(100*float((s<val).mean()),1),
             min=jn(s.min()), median=jn(s.median()), max=jn(s.max()))
    if cheap_col is not None:
        ch = S[cheap_col].iloc[-1]
        if ch==ch:
            d['cheap']=round(1-float(ch),4); d['strength']=fm.strength_index(1-float(ch))
    return d

sg = S.loc[last]
today = dict(
  date=str(last.date()), price=jn(P['close'].iloc[-1]),
  data_date_onchain=str((last-pd.Timedelta(days=2)).date()),
  scores={k: jn(v.iloc[-1]) for k,v in SCORES.items()},
  states={k: int(fm.state_index(v,k).iloc[-1]) for k,v in SCORES.items()},
  indicators=dict(
    mvrv=ctx('mvrv', sg['mvrv'], 'pct_mvrv'),
    p_ma200w=ctx('p_ma200w', sg['p_ma200w'], 'pct_p_ma200w'),
    rsi_weekly=ctx('rsi_weekly', sg['rsi_weekly'], 'pct_rsi_weekly'),
    mayer=ctx('mayer', sg['mayer'], 'pct_mayer'),
    price_to_rp=ctx('price_to_rp', sg['price_to_rp'], 'pct_price_to_rp'),
    mvrv_zscore=ctx('mvrv_zscore', sg['mvrv_zscore'], 'pct_mvrv_zscore'),
    nupl=ctx('nupl', sg['nupl'], 'pct_mvrv'),
    realized_price=ctx('realized_price', S['realized_price'].loc[last]),
    ma200d=ctx('ma200d', sg['ma200d']), ma200w=ctx('ma200w', sg['ma200w']),
  ),
  hash_ribbon=(None if sg['hash_ribbon']!=sg['hash_ribbon'] else
               ['normal','capitulacao','recuperacao'][int(sg['hash_ribbon'])]),
)

PROFILES=list(fm.PROFILE_MULTS.keys()); PERIODS={'2021':'2021-01-01','2013':'2013-01-01'}
bk={}; series={}
for src, sc in SCORES.items():
    for prof in PROFILES:
        mult = fm.multiplier(sc, prof, src)
        for pk, pstart in PERIODS.items():
            d,m,out = bt.run(P, mult, start=pstart)
            r,s,dist = bt.metrics(d,out,m)
            key=f'{src}|{prof}|{pk}'
            bk[key]=dict(days=int(s['days']),
              rows={k:{kk:jn(vv) for kk,vv in r.loc[k].items()} for k in r.index},
              extra_btc_pct=jn(s['extra_btc_pct']), avg_cost_improvement=jn(s['avg_cost_improvement']*100),
              btc_vs_A_pct=jn(s['btc_vs_A_pct']), capital_ratio=jn(s['capital_ratio_vs_A']),
              worst30=jn(s['worst30_capital']), worst90=jn(s['worst90_capital']),
              dist={str(k):jn(v) for k,v in dist.items()}, final_price=jn(s['final_price']))
            idx = d.resample('W-SUN').last().index.intersection(d.index)
            series[key]=dict(dates=[str(x.date()) for x in idx],
              btc_a=[jn(v) for v in out['A_fixed']['cum_btc'].reindex(idx)],
              btc_b=[jn(v) for v in out['B_dynamic']['cum_btc'].reindex(idx)],
              btc_c=[jn(v) for v in out['C_equal_capital']['cum_btc'].reindex(idx)],
              cap_b=[jn(v) for v in out['B_dynamic']['cum_inv'].reindex(idx)],
              avg_b=[jn(v) for v in (out['B_dynamic']['cum_inv']/out['B_dynamic']['cum_btc']).reindex(idx)],
              avg_c=[jn(v) for v in (out['C_equal_capital']['cum_inv']/out['C_equal_capital']['cum_btc']).reindex(idx)])

w = P.resample('W-SUN').last()
hist=dict(dates=[str(x.date()) for x in w.index],
  price=[jn(v) for v in w['close']], mvrv=[jn(v) for v in w['mvrv']],
  mayer=[jn(v) for v in w['mayer']], rsi=[jn(v) for v in w['rsi_weekly']],
  p200w=[jn(v) for v in w['p_ma200w']], rp=[jn(v) for v in w['realized_price']],
  nupl=[jn(v) for v in w['nupl']], zscore=[jn(v) for v in w['mvrv_zscore']],
  score_mvrv=[jn(v) for v in SCORES['mvrv'].reindex(w.index)],
  score_composto=[jn(v) for v in SCORES['composto'].reindex(w.index)],
  state_mvrv=[int(v) for v in fm.state_index(SCORES['mvrv'],'mvrv').reindex(w.index).fillna(0)],
  state_composto=[int(v) for v in fm.state_index(SCORES['composto'],'composto').reindex(w.index).fillna(0)])

roll={}
for src, sc in SCORES.items():
    m = fm.multiplier(sc,'agressivo',src)
    rw = rl.rolling_efficiency(P, m, 1460, 15, '2013-01-01')
    roll[src]=dict(eff=[jn(v) for v in rw['efficiency']],
      median=jn(rw['efficiency'].median()), win=jn(100*(rw['efficiency']>1).mean()),
      worst=jn(rw['efficiency'].min()), best=jn(rw['efficiency'].max()))

ev=dict(head_to_head=pd.read_csv('out/head_to_head.csv').to_dict('records'),
        frontier=pd.read_csv('out/frontier.csv').to_dict('records'),
        walkforward=pd.read_csv('out/walkforward.csv').to_dict('records'),
        recovery=pd.read_csv('out/recovery_test.csv').to_dict('records'),
        subsets=pd.read_csv('out/subset_sweep.csv').round(4).to_dict('records'),
        comp_wf=pd.read_csv('out/composite_walkforward.csv').to_dict('records'))

payload=dict(generated=str(pd.Timestamp.now(tz='UTC'))[:19]+' UTC', today=today, backtest=bk,
  series=series, hist=hist, rolling=roll, evidence=ev,
  model=dict(cuts=dict(mvrv=fm.CUTS_MVRV, composto=fm.CUTS_COMP),
             mvrv_bounds=fm.MVRV_BOUNDS, weights=fm.WEIGHTS,
             profiles=fm.PROFILE_MULTS, states=fm.STATES,
             strength=fm.STRENGTH, strength_cuts=fm.STRENGTH_CUTS))
os.makedirs('app',exist_ok=True)
open('out/app_data.json','w').write(json.dumps(payload,separators=(',',':')))
open('app/data.js','w').write('window.__BTCDCA='+json.dumps(payload,separators=(',',':'))+';')
print('app/data.js', f"{os.path.getsize('app/data.js'):,} bytes  |  {len(bk)} backtests")
print('hoje:', today['date'], '| scores', today['scores'], '| estados', today['states'])
print('rolling:', {k:(v['median'],v['win']) for k,v in roll.items()})
