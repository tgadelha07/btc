"""download_data.py — ENTREGAVEL 3 (reproducible data acquisition).

Network reality in this environment: the egress policy denies CONNECT to every
crypto API host tried (community-api.coinmetrics.io, api.binance.com,
api.coingecko.com, api.exchange.coinbase.com, api.blockchain.info,
min-api.cryptocompare.com, api.kraken.com, query1.finance.yahoo.com,
huggingface.co, kaggle.com, storage.googleapis.com).  GitHub IS reachable, so
every source below is fetched from a public GitHub repository.  Each is the
ORIGINAL provider's own data, not a re-derivation.

Fallback chain actually used (item 36):
  price   : Bitstamp 1-min (ff137) -> [Coin Metrics ReferenceRate] -> [blockchain.com]
  onchain : Coin Metrics community via akpasz/btc-data (daily)
            -> coinmetrics/data csv archive (same provider, stale mirror)
            -> ErcinDedeoglu/crypto-market-data (CryptoQuant, 2022+ only)
"""
import os, subprocess, sys
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw')
os.makedirs(RAW, exist_ok=True)

SOURCES = {
 # --- PRICE (single source for every transaction in every scenario) ---
 'btcusd_bitstamp_1min_2012-2025.csv.gz':
   'https://raw.githubusercontent.com/ff137/bitstamp-btcusd-minute-data/main/data/historical/btcusd_bitstamp_1min_2012-2025.csv.gz',
 'btcusd_bitstamp_1min_latest.csv':
   'https://raw.githubusercontent.com/ff137/bitstamp-btcusd-minute-data/main/data/updates/btcusd_bitstamp_1min_latest.csv',
 # --- ON-CHAIN (Coin Metrics community tier) ---
 'akpasz_coinmetrics.json':
   'https://raw.githubusercontent.com/akpasz/btc-data/main/data/coinmetrics.json',
 'akpasz_blockchain.json':
   'https://raw.githubusercontent.com/akpasz/btc-data/main/data/blockchain.json',
 # --- CROSS-CHECK MIRRORS (validation only, never spliced into the backtest) ---
 'cm_btc.csv':
   'https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv',
 'btc_mvrv_ratio.json':
   'https://raw.githubusercontent.com/ErcinDedeoglu/crypto-market-data/main/data/daily/btc_mvrv_ratio.json',
}

if __name__ == '__main__':
    for name, url in SOURCES.items():
        dest = os.path.join(RAW, name)
        print(f'-> {name}')
        subprocess.run(['curl','-sSL','-m','900','-o',dest,url], check=True)
        print(f'   {os.path.getsize(dest):,} bytes')
    print('\nNext: python3 src/build_price.py && python3 src/calculate_indicators.py')
