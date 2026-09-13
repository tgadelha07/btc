"""optimize.py — controlled grid search over thresholds and multipliers (item 13)."""
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

def quick(mult,horizon=1460,step=30,start='2013-01-01'):
    rw=rl.rolling_efficiency(P,mult,horizon_days=horizon,step_days=step,start=start)
    e=rw['efficiency']
    return e.median(), 100*(e>1).mean(), e.quantile(0.05), rw['capital_x'].median()

if __name__=='__main__':
    T1=[1.6,1.5,1.4,1.3,1.2]; T2=[1.2,1.1,1.05,1.0]; T3=[1.0,0.95,0.9,0.85]; T4=[0.9,0.85,0.8,0.75]
    rows=[]
    for t1,t2,t3,t4 in itertools.product(T1,T2,T3,T4):
        if not (t1>t2>t3>t4): continue
        for pname,mm in PROFILES.items():
            m=ladder('mvrv',[t1,t2,t3,t4],mm)
            med,win,p05,cap=quick(m)
            e21=an.efficiency(m,start='2021-01-01')
            rows.append(dict(t1=t1,t2=t2,t3=t3,t4=t4,perfil=pname,
                             eff_mediana=med,win=win,p05=p05,capital_x=cap,eff_2021=e21))
    g=pd.DataFrame(rows); g.to_csv('out/grid_mvrv.csv',index=False)
    pd.set_option('display.width',250)
    print('GRID MVRV — %d combinacoes'%len(g))
    print('\nTOP 15 por eficiencia mediana (janelas 4a, 2013-2026):')
    print(g.sort_values('eff_mediana',ascending=False).head(15).to_string(index=False,float_format=lambda x:f'{x:.4f}'))
    print('\nTOP 15 por eficiencia POR UNIDADE DE CAPITAL EXTRA  [(eff-1)/(capital_x-1)]:')
    g['eficiencia_do_capital']=(g['eff_mediana']-1)/(g['capital_x']-1)
    print(g.sort_values('eficiencia_do_capital',ascending=False).head(15).to_string(index=False,float_format=lambda x:f'{x:.4f}'))
    print('\nMelhor por perfil de multiplicador:')
    print(g.loc[g.groupby('perfil')['eff_mediana'].idxmax()].to_string(index=False,float_format=lambda x:f'{x:.4f}'))
