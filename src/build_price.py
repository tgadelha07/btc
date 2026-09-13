import pandas as pd, numpy as np, gzip, os
RAW='/home/claude/btcdca/raw'
usecols=['timestamp','open','high','low','close','volume']
dt={'timestamp':'int64','open':'float64','high':'float64','low':'float64','close':'float64','volume':'float64'}

def agg(path, compression=None):
    out=[]
    for ch in pd.read_csv(path, usecols=usecols, dtype=dt, compression=compression, chunksize=1_000_000):
        ch['date']=pd.to_datetime(ch['timestamp'], unit='s', utc=True).dt.floor('D')
        ch['pv']=ch['close']*ch['volume']
        g=ch.groupby('date').agg(open=('open','first'),high=('high','max'),low=('low','min'),
                                 close=('close','last'),volume=('volume','sum'),pv=('pv','sum'),
                                 n=('close','size'))
        out.append(g)
    d=pd.concat(out)
    # chunk boundaries can split a day -> re-aggregate
    d=d.groupby(level=0).agg(open=('open','first'),high=('high','max'),low=('low','min'),
                             close=('close','last'),volume=('volume','sum'),pv=('pv','sum'),n=('n','sum'))
    return d

h=agg(os.path.join(RAW,'btcusd_bitstamp_1min_2012-2025.csv.gz'), compression='gzip')
print('historical days:', len(h), h.index.min().date(), h.index.max().date())
l=agg(os.path.join(RAW,'btcusd_bitstamp_1min_latest.csv'))
print('latest days:', len(l), l.index.min().date(), l.index.max().date())

# overlap day: historical ends mid-day 2025-01-07 -> merge the two halves of that day
both=pd.concat([h,l])
d=both.groupby(level=0).agg(open=('open','first'),high=('high','max'),low=('low','min'),
                            close=('close','last'),volume=('volume','sum'),pv=('pv','sum'),n=('n','sum'))
d.index.name='date'
d['vwap']=np.where(d['volume']>0, d['pv']/d['volume'], np.nan)
d['ohlc4']=(d['open']+d['high']+d['low']+d['close'])/4.0
d=d.drop(columns=['pv'])
d.to_csv('/home/claude/btcdca/data/btc_daily_bitstamp.csv')
print('\nMERGED:', len(d), d.index.min().date(), '->', d.index.max().date())
print('missing calendar days:', len(pd.date_range(d.index.min(), d.index.max(), freq='D', tz='UTC').difference(d.index)))
print('days with n != 1440:', int((d['n']!=1440).sum()))
print(d.head(3)[['open','high','low','close','volume','vwap','ohlc4','n']])
print(d.tail(3)[['open','high','low','close','volume','vwap','ohlc4','n']])
