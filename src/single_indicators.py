import sys; sys.path.insert(0,'src')
import numpy as np, pandas as pd, analyze as an

PANEL, SIG = an.PANEL, an.SIG

def circ_p(mult, start, end=None, step=7):
    """Circular-shift null: does the signal beat itself placed at other times?
       Controls for the fact that ANY early-weighted scheme wins in an uptrend."""
    d = an.slice_(start, end)
    w = mult.reindex(d.index).fillna(1.0).to_numpy(float)
    inv = 1.0/d['ohlc4'].to_numpy(float); base = inv.mean(); n=len(w)
    actual = (w*inv).sum()/w.sum()/base
    effs=[]
    for k in range(0, n, step):
        ww = np.roll(w, k)
        effs.append((ww*inv).sum()/ww.sum()/base)
    effs=np.array(effs)
    return actual, float((effs >= actual).mean()), float(np.median(effs)), float(effs.max())

SPECS = [
 ('Mayer Multiple',      'mayer',       [1.0,0.9,0.8,0.7,0.6]),
 ('MVRV',                'mvrv',        [1.5,1.2,1.1,1.0,0.9,0.8]),
 ('Preco/Realized Price','price_to_rp', [1.5,1.2,1.1,1.0,0.9,0.8]),
 ('Preco/MM200W',        'p_ma200w',    [2.0,1.5,1.2,1.0,0.9,0.8]),
 ('RSI semanal',         'rsi_weekly',  [45,40,35,30,25]),
 ('NUPL',                'nupl',        [0.35,0.2,0.1,0.0,-0.1]),
 ('MVRV Z (percentil)',  'pct_mvrv_zscore',[0.35,0.25,0.15,0.10,0.05]),
 ('MVRV (percentil)',    'pct_mvrv',    [0.35,0.25,0.15,0.10,0.05]),
]

PERIODS = [('TREINO 2013-2020','2013-01-01','2020-12-31'),
           ('TESTE 2021-2026','2021-01-01',None),
           ('COMPLETO 2013-2026','2013-01-01',None)]

rows=[]
for label, col, ths in SPECS:
    for t in ths:
        sig = (SIG[col] < t).fillna(False)
        rec={'indicador':label,'coluna':col,'threshold':t}
        for pl,s,e in PERIODS:
            L,f = an.lift(sig, s, e)
            rec[f'{pl}|freq%'] = round(100*f,1)
            rec[f'{pl}|lift']  = round(L,4) if L==L else np.nan
            rec[f'{pl}|eff@2x']= round(an.eff_from_lift(L,f,2.0),4) if L==L else np.nan
        rows.append(rec)

# Hash ribbon capitulation (binary)
for label, sig in [('Hash Ribbons capitulacao', (SIG['hr_capitulation']==1).fillna(False)),
                   ('Hash Ribbons recovery30d', (SIG['hash_ribbon']==2).fillna(False))]:
    rec={'indicador':label,'coluna':'hash_ribbon','threshold':np.nan}
    for pl,s,e in PERIODS:
        L,f=an.lift(sig,s,e)
        rec[f'{pl}|freq%']=round(100*f,1); rec[f'{pl}|lift']=round(L,4) if L==L else np.nan
        rec[f'{pl}|eff@2x']=round(an.eff_from_lift(L,f,2.0),4) if L==L else np.nan
    rows.append(rec)

res=pd.DataFrame(rows)
res.to_csv('out/single_indicator_lift.csv', index=False)
pd.set_option('display.width',250)
for pl,_,_ in PERIODS:
    print('='*110); print('PERIODO:', pl)
    sub=res[['indicador','threshold',f'{pl}|freq%',f'{pl}|lift',f'{pl}|eff@2x']].copy()
    sub.columns=['indicador','thr','freq%','lift','eff@2x']
    sub=sub[sub['freq%']>1.0]
    print(sub.sort_values('lift',ascending=False).head(18).to_string(index=False))
