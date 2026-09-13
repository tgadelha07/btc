"""Shared analysis helpers: capital-neutral edge decomposition."""
import numpy as np, pandas as pd, sys
sys.path.insert(0,'src')
import backtest as bt

PANEL = pd.read_csv('data/master_panel.csv', parse_dates=['date']).set_index('date')
SIG   = bt.make_signal_frame(PANEL)

def slice_(start=None, end=None):
    d = PANEL
    if start: d = d[d.index >= pd.Timestamp(start)]
    if end:   d = d[d.index <= pd.Timestamp(end)]
    return d

def efficiency(mult, start=None, end=None, price_col='ohlc4'):
    """BTC efficiency of a weighting scheme vs equal-capital uniform DCA.
       Identity: eff = E_w[1/p] / E[1/p]  (capital is held identical by construction)."""
    d = slice_(start, end)
    w = mult.reindex(d.index).fillna(1.0).to_numpy(float)
    inv_p = 1.0 / d[price_col].to_numpy(float)
    return float((w*inv_p).sum()/w.sum() / inv_p.mean())

def lift(signal, start=None, end=None, price_col='ohlc4'):
    """E[1/p | signal] / E[1/p]  -- multiplier-free measure of an indicator's edge.
       >1 means the signal preferentially fires on days that buy more BTC per dollar."""
    d = slice_(start, end)
    s = signal.reindex(d.index).fillna(False).to_numpy(bool)
    inv_p = 1.0/d[price_col].to_numpy(float)
    if s.sum() == 0: return np.nan, 0.0
    return float(inv_p[s].mean()/inv_p.mean()), float(s.mean())

def eff_from_lift(L, f, M):
    """Closed form: binary signal firing on fraction f with lift L, multiplier M."""
    return (1 + (M-1)*f*L) / (1 + (M-1)*f)
