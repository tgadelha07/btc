"""
calculate_indicators.py — BTC DYNAMIC DCA
Builds the master daily panel from:
  * data/btc_daily_bitstamp.csv  (price, single source for ALL transactions)
  * raw/akpasz_coinmetrics.json  (Coin Metrics community tier, on-chain)

ALL indicators are point-in-time. No full-sample statistic is ever used.
Look-ahead is handled downstream in backtest.py by explicit lags; this file
only produces "value known as of the close of day D".
"""
import json, numpy as np, pandas as pd, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, 'raw'); DATA = os.path.join(BASE, 'data')

# ---------------------------------------------------------------- price
px = pd.read_csv(os.path.join(DATA, 'btc_daily_bitstamp.csv'), parse_dates=['date'])
px['date'] = px['date'].dt.tz_localize(None)
px = px.set_index('date').sort_index()
px = px[px['n'] >= 1400]                      # drop incomplete days (today)
px = px.rename(columns={'close': 'close', 'ohlc4': 'ohlc4', 'vwap': 'vwap'})

# ---------------------------------------------------------------- on-chain
cmj = json.load(open(os.path.join(RAW, 'akpasz_coinmetrics.json')))
cm = pd.DataFrame({k: pd.Series({pd.Timestamp(a): b for a, b in v})
                   for k, v in cmj['series'].items()}).sort_index()
# mirror ships dates shifted +1d vs Coin Metrics' native convention; undo it
# (verified: -1d reproduces coinmetrics/data/csv/btc.csv to 4.4e-16 over 4161 days)
cm.index = cm.index - pd.Timedelta(days=1)
cm.index.name = 'date'

df = px.join(cm[['CapMVRVCur', 'CapMrktCurUSD', 'SplyCur', 'HashRate', 'PriceUSD']], how='left')
df = df.rename(columns={'CapMVRVCur': 'mvrv', 'CapMrktCurUSD': 'market_cap',
                        'SplyCur': 'supply', 'HashRate': 'hashrate',
                        'PriceUSD': 'cm_price'})

# ---------------------------------------------------------------- derived on-chain
df['realized_cap']   = df['market_cap'] / df['mvrv']
df['realized_price'] = df['realized_cap'] / df['supply']
df['price_to_rp']    = df['close'] / df['realized_price']
# NUPL is an exact algebraic identity of MVRV: (MC-RC)/MC = 1 - 1/MVRV
df['nupl']           = 1.0 - 1.0 / df['mvrv']

# MVRV Z-score, POINT-IN-TIME: expanding std of market cap (never full-sample)
mc = df['market_cap']
df['mvrv_zscore'] = (mc - df['realized_cap']) / mc.expanding(min_periods=365).std()

# ---------------------------------------------------------------- price indicators
c = df['close']
df['ma200d'] = c.rolling(200, min_periods=200).mean()
df['mayer']  = c / df['ma200d']
df['ma200w'] = c.rolling(1400, min_periods=1400).mean()     # 200 weeks of daily closes
df['p_ma200w'] = c / df['ma200w']

# Weekly RSI(14) Wilder, on COMPLETED weeks only (week ends Sunday UTC)
wk = c.resample('W-SUN').last()
wk_complete = wk.copy()
d_ = wk_complete.diff()
gain = d_.clip(lower=0); loss = -d_.clip(upper=0)
ag = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
al = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
rsi_w = 100 - 100 / (1 + ag / al.replace(0, np.nan))
# map each completed week to the days that follow its close (no look-ahead)
rsi_daily = rsi_w.copy()
rsi_daily.index = rsi_daily.index  # index = Sunday = day the week closed
df['rsi_weekly'] = rsi_daily.reindex(df.index, method='ffill')
df['rsi_weekly_prev'] = rsi_w.shift(1).reindex(df.index, method='ffill')

# Hash Ribbons (Capriole): MA30 vs MA60 of hashrate
hr = df['hashrate']
df['hr_ma30'] = hr.rolling(30, min_periods=30).mean()
df['hr_ma60'] = hr.rolling(60, min_periods=60).mean()
df['hr_capitulation'] = (df['hr_ma30'] < df['hr_ma60']).astype(float)
cap_prev = df['hr_capitulation'].shift(1)
df['hr_recovery'] = ((df['hr_capitulation'] == 0) & (cap_prev == 1)).astype(float)
# hash_ribbon state: 1 = capitulation, 2 = first 30d after recovery cross, 0 = normal
rec = df['hr_recovery'].rolling(30, min_periods=1).max().fillna(0)
df['hash_ribbon'] = np.where(df['hr_capitulation'] == 1, 1.0,
                      np.where(rec == 1, 2.0, 0.0))
df.loc[df['hr_ma60'].isna(), 'hash_ribbon'] = np.nan

# ---------------------------------------------------------------- point-in-time percentiles
def expanding_pct(s, min_periods=365):
    """% of prior-and-current observations strictly below today's value."""
    v = s.to_numpy(dtype=float); out = np.full(len(v), np.nan)
    import bisect
    srt = []
    for i, x in enumerate(v):
        if np.isnan(x):
            continue
        if len(srt) >= min_periods:
            out[i] = bisect.bisect_left(srt, x) / len(srt)
        bisect.insort(srt, x)
    return pd.Series(out, index=s.index)

for col in ['mvrv', 'mayer', 'p_ma200w', 'price_to_rp', 'rsi_weekly', 'mvrv_zscore']:
    df[f'pct_{col}'] = expanding_pct(df[col])

df.to_csv(os.path.join(DATA, 'master_panel.csv'))
print('master panel:', df.shape, df.index.min().date(), '->', df.index.max().date())
cov = pd.DataFrame({'first': df.apply(lambda s: s.first_valid_index()),
                    'last':  df.apply(lambda s: s.last_valid_index()),
                    'n':     df.notna().sum()})
print(cov.to_string())
