"""Opportunity Score architecture + subset sweep (items 14, 18, 19)."""
import numpy as np, pandas as pd, itertools, sys
sys.path.insert(0,'src')
import analyze as an, rolling as rl

S, P = an.SIG, an.PANEL

# each component -> point-in-time 'cheapness' in [0,1] (1 = historically cheapest)
COMP = {
 'MVRV'   : (1 - S['pct_mvrv']),
 'Mayer'  : (1 - S['pct_mayer']),
 'MM200W' : (1 - S['pct_p_ma200w']),
 'RSI'    : (1 - S['pct_rsi_weekly']),
 'HashR'  : (S['hr_capitulation'] == 1).astype(float).where(S['hr_capitulation'].notna()),
 'RealP'  : (1 - S['pct_price_to_rp']),
 'MVRVz'  : (1 - S['pct_mvrv_zscore']),
}

def build_score(names, weights=None):
    """Weighted mean of available components; weights renormalised over what exists
       on each day, so a metric that does not yet have history never blocks the score."""
    cols = pd.DataFrame({n: COMP[n] for n in names})
    w = pd.Series(weights if weights else {n: 1.0 for n in names})
    mask = cols.notna()
    wmat = mask.mul(w, axis=1)
    denom = wmat.sum(axis=1)
    score = (cols.fillna(0) * wmat).sum(axis=1) / denom.replace(0, np.nan)
    return (score * 100).rename('opportunity_score')

def score_to_mult_steps(score, cuts=(60,72,82,90), mults=(1.5,2.0,3.0,4.0)):
    m = pd.Series(1.0, index=score.index)
    for c, mu in zip(cuts, mults):
        m[(score >= c).fillna(False)] = mu
    return m

def score_to_mult_cont(score, floor=55.0, mmax=4.0, gamma=1.0):
    x = ((score - floor) / (100.0 - floor)).clip(lower=0, upper=1)
    return (1.0 + (mmax - 1.0) * x.pow(gamma)).fillna(1.0)

def evaluate(mult, horizon=1460, step=30, start='2013-01-01'):
    rw = rl.rolling_efficiency(P, mult, horizon_days=horizon, step_days=step, start=start)
    wr = rl.window_shift_rank(P, mult, horizon_days=horizon, step_days=120,
                              start=start, shift_step=10)
    e = rw['efficiency']
    return dict(eff_mediana=e.median(), pct_janelas_win=100*(e>1).mean(),
                eff_p05=e.quantile(0.05), eff_pior=e.min(),
                rank_mediano=wr['rank'].median(),
                capital_x=rw['capital_x'].median(),
                eff_2021=an.efficiency(mult, start='2021-01-01'))
