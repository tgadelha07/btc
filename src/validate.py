"""validate.py — out-of-sample discipline (items 16, 17).
Walk-forward: choose parameters using ONLY data available at the decision date,
then measure what those parameters earned afterwards. Compared against a fixed
naive rule to test whether optimisation adds anything beyond noise."""
import sys; sys.path.insert(0,'src')
import numpy as np, pandas as pd, itertools
import analyze as an, rolling as rl
S,P=an.SIG,an.PANEL
PROFILES={'conservador':(1.25,1.5,2.0,3.0),'moderado':(1.5,2.0,2.5,3.0),
          'agressivo':(1.5,2.0,3.0,4.0),'muito agressivo':(2.0,3.0,4.0,5.0)}

def ladder(col,ths,mults):
    m=pd.Series(1.0,index=S.index); x=S[col]
    for t,mu in zip(ths,mults): m[(x<t).fillna(False)]=mu
    return m

GRID=[]
for t1,t2,t3,t4 in itertools.product([1.6,1.5,1.4,1.3,1.2],[1.2,1.1,1.05,1.0],
                                     [1.0,0.95,0.9,0.85],[0.9,0.85,0.8,0.75]):
    if t1>t2>t3>t4:
        for pn,mm in PROFILES.items(): GRID.append((t1,t2,t3,t4,pn,mm))

def eff_window(mult,a,b):
    d=P[(P.index>=pd.Timestamp(a))&(P.index<pd.Timestamp(b))]
    if len(d)<200: return np.nan
    w=mult.reindex(d.index).fillna(1.0).to_numpy(float); iv=1/d['ohlc4'].to_numpy(float)
    return (w*iv).sum()/w.sum()/iv.mean()

def insample_score(mult,train_end,horizon=1095):
    rw=rl.rolling_efficiency(P[P.index<pd.Timestamp(train_end)],mult,
                             horizon_days=horizon,step_days=30,start='2013-01-01')
    return rw['efficiency'].median() if len(rw) else np.nan

if __name__=='__main__':
    DEFAULT=ladder('mvrv',[1.2,1.0,0.9,0.8],PROFILES['agressivo'])
    rows=[]
    for y in range(2017,2026):
        tr_end=f'{y}-01-01'; te_end=f'{min(y+2,2027)}-01-01'
        best=None
        for t1,t2,t3,t4,pn,mm in GRID:
            m=ladder('mvrv',[t1,t2,t3,t4],mm)
            sc=insample_score(m,tr_end)
            if sc==sc and (best is None or sc>best[0]): best=(sc,(t1,t2,t3,t4,pn,mm),m)
        if best is None: continue
        sc,params,m=best
        rows.append(dict(treino_ate=tr_end[:4], teste=f'{y}-{min(y+2,2027)}',
            params=f'{params[0]}/{params[1]}/{params[2]}/{params[3]} {params[4]}',
            IS_eff=round(sc,4),
            OOS_otimizado=round(eff_window(m,tr_end,te_end),4),
            OOS_regra_fixa=round(eff_window(DEFAULT,tr_end,te_end),4)))
    w=pd.DataFrame(rows)
    w['otim_menos_fixa']=(w['OOS_otimizado']-w['OOS_regra_fixa']).round(4)
    pd.set_option('display.width',250)
    print('WALK-FORWARD — otimizar so com dados anteriores, medir nos 2 anos seguintes')
    print(w.to_string(index=False))
    print()
    print(f"OOS medio  otimizado : {w['OOS_otimizado'].mean():.4f}   (>1 = bateu o DCA uniforme de mesmo capital)")
    print(f"OOS medio  regra fixa: {w['OOS_regra_fixa'].mean():.4f}")
    print(f"Vantagem da otimizacao: {w['otim_menos_fixa'].mean():+.4f}  | venceu em {int((w['otim_menos_fixa']>0).sum())}/{len(w)} janelas")
    w.to_csv('out/walkforward.csv',index=False)
