"""Rolling-window evaluation: the honest way to score a DCA overlay.

A single 14-year window is dominated by its earliest days (E[1/p] is ~65%
concentrated in 2013 for a 2013-2020 window), so 'beat uniform DCA' over one
long window mostly measures how early the scheme front-loads, not skill.
We therefore score every strategy over MANY overlapping investor-length
windows and report the distribution.
"""
import numpy as np, pandas as pd

def rolling_efficiency(panel, mult, horizon_days=1460, step_days=30,
                       start='2013-01-01', price_col='ohlc4'):
    d = panel[panel.index >= pd.Timestamp(start)]
    inv = 1.0/d[price_col].to_numpy(float)
    w   = mult.reindex(d.index).fillna(1.0).to_numpy(float)
    n = len(d)
    c_inv = np.concatenate([[0], np.cumsum(inv)])
    c_w   = np.concatenate([[0], np.cumsum(w)])
    c_wi  = np.concatenate([[0], np.cumsum(w*inv)])
    starts = np.arange(0, n-horizon_days+1, step_days)
    ends   = starts + horizon_days
    num = (c_wi[ends]-c_wi[starts]) / (c_w[ends]-c_w[starts])
    den = (c_inv[ends]-c_inv[starts]) / horizon_days
    eff = num/den
    cap = (c_w[ends]-c_w[starts])/horizon_days      # mean multiplier = capital ratio vs 1x
    return pd.DataFrame({'start': d.index[starts], 'end': d.index[ends-1],
                         'efficiency': eff, 'capital_x': cap})

def summarize(rw, label=''):
    e = rw['efficiency']
    return dict(label=label, n=len(rw), median=e.median(), mean=e.mean(),
                pct_win=100*(e>1).mean(), p05=e.quantile(0.05), p25=e.quantile(0.25),
                p75=e.quantile(0.75), worst=e.min(), best=e.max(),
                capital_x=rw['capital_x'].median())

def circ_shift_null(panel, mult, start, end=None, step=5, price_col='ohlc4'):
    d = panel[panel.index >= pd.Timestamp(start)]
    if end is not None: d = d[d.index <= pd.Timestamp(end)]
    inv = 1.0/d[price_col].to_numpy(float); base = inv.mean()
    w = mult.reindex(d.index).fillna(1.0).to_numpy(float); n=len(w)
    actual = (w*inv).sum()/w.sum()/base
    effs = np.array([ (np.roll(w,k)*inv).sum()/w.sum()/base for k in range(0,n,step) ])
    return dict(actual=actual, p_value=float((effs>=actual).mean()),
                null_median=float(np.median(effs)), null_p95=float(np.quantile(effs,0.95)))

def window_shift_rank(panel, mult, horizon_days=1460, step_days=60,
                      start='2013-01-01', shift_step=7, price_col='ohlc4'):
    """For each window, rank the strategy's efficiency inside the distribution of
       the SAME weight pattern circularly shifted within that window.
       Rank near 1.0 = the signal is aligned with cheap days, not merely front-loaded."""
    import numpy as np, pandas as pd
    d = panel[panel.index >= pd.Timestamp(start)]
    inv = 1.0/d[price_col].to_numpy(float)
    w   = mult.reindex(d.index).fillna(1.0).to_numpy(float)
    n = len(d); out=[]
    for s in range(0, n-horizon_days+1, step_days):
        iv = inv[s:s+horizon_days]; ww = w[s:s+horizon_days]; base = iv.mean()
        act = (ww*iv).sum()/ww.sum()/base
        nul = np.array([ (np.roll(ww,k)*iv).sum()/ww.sum()/base
                         for k in range(0, horizon_days, shift_step) ])
        out.append(dict(start=d.index[s], end=d.index[s+horizon_days-1],
                        efficiency=act, rank=float((nul<act).mean()),
                        null_median=float(np.median(nul))))
    return pd.DataFrame(out)
