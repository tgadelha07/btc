"""
backtest.py — BTC DYNAMIC DCA engine.

Core contract (look-ahead prevention):
  A signal computed from data up to and including the close of day D may only
  change the purchase made on day D+lag, lag >= 1. Price-derived indicators use
  LAG_PRICE (default 1). On-chain indicators use LAG_ONCHAIN (default 2) to
  absorb publication delay of the Coin Metrics community feed.

Every strategy buys EVERY calendar day at the same price definition (OHLC4).
"""
import numpy as np, pandas as pd

BUY_PRICE_COL = 'ohlc4'
LAG_PRICE   = 1
LAG_ONCHAIN = 2

PRICE_COLS   = ['mayer','ma200d','ma200w','p_ma200w','rsi_weekly','rsi_weekly_prev',
                'pct_mayer','pct_p_ma200w','pct_rsi_weekly','close']
ONCHAIN_COLS = ['mvrv','mvrv_zscore','realized_price','price_to_rp','nupl','hash_ribbon',
                'hr_capitulation','pct_mvrv','pct_price_to_rp','pct_mvrv_zscore']

def make_signal_frame(panel, lag_price=LAG_PRICE, lag_onchain=LAG_ONCHAIN):
    """Return a frame where row D holds only information an investor had before buying on D."""
    s = pd.DataFrame(index=panel.index)
    for c in PRICE_COLS:
        if c in panel: s[c] = panel[c].shift(lag_price)
    for c in ONCHAIN_COLS:
        if c in panel: s[c] = panel[c].shift(lag_onchain)
    # price_to_rp mixes a price (lag 1 ok) with realized price (on-chain): use the stricter lag
    if 'realized_price' in panel and 'close' in panel:
        s['price_to_rp'] = panel['close'].shift(lag_price) / panel['realized_price'].shift(lag_onchain)
    return s

# ---------------------------------------------------------------- rules
def rule_h0(s):
    """Hypothesis zero from the brief (section 2), made explicit.
       RSI 'deprimido' := weekly RSI < 35. 'capitulacao extrema' := hash-ribbon
       miner capitulation OR price below the 200-week MA."""
    m = pd.Series(1.0, index=s.index)
    mayer, mvrv, rsi = s['mayer'], s['mvrv'], s['rsi_weekly']
    below200w = (s['p_ma200w'] < 1.0).fillna(False)
    capit = (s['hr_capitulation'] == 1).fillna(False) | below200w
    m[(mayer < 0.8).fillna(False)] = 1.5
    m[((mayer < 0.8) & (mvrv < 1.0)).fillna(False)] = 2.0
    m[((mayer < 0.8) & (mvrv < 1.0) & ((rsi < 35) | below200w)).fillna(False)] = 3.0
    m[((mayer < 0.6) & (mvrv < 0.8) & capit).fillna(False)] = 4.0
    return m

def rule_threshold(s, col, thresholds, mults):
    """Generic monotone single-indicator ladder. thresholds descending, mults ascending."""
    m = pd.Series(1.0, index=s.index)
    x = s[col]
    for t, mu in zip(thresholds, mults):
        m[(x < t).fillna(False)] = mu
    return m

# ---------------------------------------------------------------- engine
def run(panel, multiplier, start=None, end=None, fee=0.0, base=100.0):
    """multiplier: Series aligned to panel.index (already lagged / look-ahead safe)."""
    d = panel.copy()
    if start is not None: d = d[d.index >= pd.Timestamp(start)]
    if end   is not None: d = d[d.index <= pd.Timestamp(end)]
    p = d[BUY_PRICE_COL].astype(float)
    mult = multiplier.reindex(d.index).fillna(1.0).astype(float)
    n = len(d)

    inv_dyn = base * mult
    inv_fix = pd.Series(base, index=d.index)
    equal   = pd.Series(inv_dyn.sum() / n, index=d.index)

    out = {}
    for name, inv in [('A_fixed', inv_fix), ('B_dynamic', inv_dyn), ('C_equal_capital', equal)]:
        btc = (inv * (1.0 - fee)) / p
        out[name] = dict(invested=inv, btc=btc, cum_inv=inv.cumsum(), cum_btc=btc.cumsum())
    return d, mult, out

def metrics(d, out, mult, base=100.0):
    p_final = float(d['close'].iloc[-1])
    n = len(d)
    rows = {}
    for name, o in out.items():
        cap  = float(o['cum_inv'].iloc[-1]); btc = float(o['cum_btc'].iloc[-1])
        val  = btc * p_final
        # portfolio max drawdown on mark-to-market value vs cumulative peak
        mtm  = o['cum_btc'] * d['close']
        dd   = (mtm / mtm.cummax() - 1.0).min()
        rows[name] = dict(capital=cap, btc=btc, avg_price=cap/btc, final_value=val,
                          profit=val-cap, roi=(val-cap)/cap, max_dd=float(dd),
                          max_daily=float(o['invested'].max()),
                          mean_daily=float(o['invested'].mean()),
                          p95_daily=float(o['invested'].quantile(0.95)))
    r = pd.DataFrame(rows).T
    b, c = r.loc['B_dynamic'], r.loc['C_equal_capital']
    summary = dict(
        days=n,
        btc_efficiency=b['btc']/c['btc'],
        extra_btc_pct=100*(b['btc']/c['btc']-1),
        avg_cost_improvement=1-b['avg_price']/c['avg_price'],
        capital_ratio_vs_A=b['capital']/r.loc['A_fixed','capital'],
        btc_vs_A_pct=100*(b['btc']/r.loc['A_fixed','btc']-1),
        worst30_capital=float((base*mult).rolling(30).sum().max()),
        worst90_capital=float((base*mult).rolling(90).sum().max()),
        final_price=p_final,
    )
    dist = mult.value_counts().sort_index()
    dist = (dist/len(mult)*100).round(2)
    return r, summary, dist
