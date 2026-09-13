"""update_daily.py — atualizacao incremental diaria.

Baixa so o que mudou:
  * Coin Metrics community (JSON, ~1,7 MB) — serie on-chain completa, sempre inteira.
  * Bitstamp 1-min: pede apenas a CAUDA do arquivo por HTTP Range (~3 MB em vez
    de 49 MB) e refaz os ultimos dias; cai para download completo se o servidor
    nao aceitar Range.

O historico diario fica cacheado em data/btc_daily_bitstamp.csv e so recebe os
dias novos. Rode src/bootstrap.py uma unica vez para criar esse cache.
"""
import os, io, sys, subprocess
import pandas as pd, numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE,'raw'); DATA = os.path.join(BASE,'data')
os.makedirs(RAW, exist_ok=True); os.makedirs(DATA, exist_ok=True)

CM_URL   = 'https://raw.githubusercontent.com/akpasz/btc-data/main/data/coinmetrics.json'
TAIL_URL = 'https://raw.githubusercontent.com/ff137/bitstamp-btcusd-minute-data/main/data/updates/btcusd_bitstamp_1min_latest.csv'
TAIL_BYTES = 3_500_000          # ~60 mil minutos ~ 40 dias

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(cmd+'\n'+r.stderr[:500])
    return r.stdout

def fetch_price_tail():
    dest = os.path.join(RAW,'bitstamp_tail.csv')
    try:
        sh(f'curl -sSL -m 300 -H "Range: bytes=-{TAIL_BYTES}" -o "{dest}" "{TAIL_URL}"')
        txt = open(dest, encoding='utf-8', errors='ignore').read()
        if len(txt) < 1000: raise RuntimeError('cauda vazia')
        # a primeira linha quase certamente esta cortada ao meio
        txt = txt.split('\n',1)[1]
        df = pd.read_csv(io.StringIO('timestamp,open,high,low,close,volume\n'+txt),
                         on_bad_lines='skip')
        if len(df) < 500: raise RuntimeError('poucas linhas na cauda')
        print(f'  cauda por Range: {len(df):,} minutos')
        return df
    except Exception as e:
        print(f'  Range falhou ({e}); baixando arquivo inteiro')
        sh(f'curl -sSL -m 900 -o "{dest}" "{TAIL_URL}"')
        return pd.read_csv(dest)

def main():
    print('1) Coin Metrics')
    sh(f'curl -sSL -m 300 -o "{os.path.join(RAW,"akpasz_coinmetrics.json")}" "{CM_URL}"')
    print(f'   {os.path.getsize(os.path.join(RAW,"akpasz_coinmetrics.json")):,} bytes')

    print('2) Bitstamp (cauda)')
    m = fetch_price_tail()
    m = m.dropna(subset=['timestamp'])
    m['timestamp'] = m['timestamp'].astype('int64')
    m['date'] = pd.to_datetime(m['timestamp'], unit='s', utc=True).dt.floor('D')
    m['pv'] = m['close']*m['volume']
    g = m.groupby('date').agg(open=('open','first'),high=('high','max'),low=('low','min'),
                              close=('close','last'),volume=('volume','sum'),
                              pv=('pv','sum'),n=('close','size'))
    g['vwap'] = np.where(g['volume']>0, g['pv']/g['volume'], np.nan)
    g['ohlc4'] = (g['open']+g['high']+g['low']+g['close'])/4.0
    g = g.drop(columns=['pv'])

    cache = os.path.join(DATA,'btc_daily_bitstamp.csv')
    if not os.path.exists(cache):
        sys.exit('data/btc_daily_bitstamp.csv nao existe — rode src/bootstrap.py uma vez.')
    old = pd.read_csv(cache, parse_dates=['date']).set_index('date')
    if old.index.tz is None: old.index = old.index.tz_localize('UTC')
    # a cauda manda nos dias que ela cobre por inteiro; o primeiro dia dela pode estar truncado
    full = g[g['n'] >= 1400]
    merged = pd.concat([old[~old.index.isin(full.index)], full]).sort_index()
    merged.index.name='date'
    novos = len(merged) - len(old)
    merged.to_csv(cache)
    print(f'   dias no cache: {len(merged):,} (+{novos}) — ate {merged.index.max().date()}')

    print('3) indicadores + dados do app + site')
    for step in ['calculate_indicators.py','build_app_data.py','build_site.py']:
        print('   ->', step)
        sh(f'cd "{BASE}" && python3 src/{step}')
    print('pronto.')

if __name__ == '__main__':
    main()
