"""composite.py — Opportunity Score composto (MVRV, Mayer, RSI semanal, MM200W).

Cada componente entra como 'barateza' point-in-time = 1 - percentil expanding.
Pesos renormalizados sobre os componentes disponiveis em cada dia, para que a
MM200W (que so existe a partir de 31/10/2015) nunca bloqueie o score.
"""
import sys; sys.path.insert(0,'src')
import numpy as np, pandas as pd, itertools
import analyze as an, rolling as rl
S,P = an.SIG, an.PANEL

COMPONENTS = {
 'MVRV'  : 1 - S['pct_mvrv'],
 'Mayer' : 1 - S['pct_mayer'],
 'RSI'   : 1 - S['pct_rsi_weekly'],
 'MM200W': 1 - S['pct_p_ma200w'],
}
NAMES = list(COMPONENTS.keys())
_COLS = pd.DataFrame(COMPONENTS)
_MASK = _COLS.notna()

def score(weights):
    w = pd.Series(weights, index=NAMES, dtype=float)
    wm = _MASK.mul(w, axis=1)
    den = wm.sum(axis=1)
    return ((_COLS.fillna(0)*wm).sum(axis=1)/den.replace(0,np.nan))*100

def mult_from_score(sc, cuts, mults):
    m = pd.Series(1.0, index=sc.index)
    for c, mu in zip(cuts, mults): m[(sc>=c).fillna(False)] = mu
    return m

def evaluate(m, start='2013-01-01', H=1460, step=30):
    rw = rl.rolling_efficiency(P, m, H, step, start)
    e = rw['efficiency']
    return dict(eff=e.median(), win=100*(e>1).mean(), p05=e.quantile(0.05),
                pior=e.min(), cap=rw['capital_x'].median())
