"""bootstrap.py — execucao unica: monta o cache diario a partir do arquivo
historico completo da Bitstamp (94 MB comprimidos, 7,9 milhoes de candles).
Depois disso, use apenas src/update_daily.py."""
import os, subprocess, sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for s in ['download_data.py','build_price.py','calculate_indicators.py','build_app_data.py','build_site.py']:
    print('->',s); 
    r=subprocess.run(f'cd "{BASE}" && python3 src/{s}',shell=True)
    if r.returncode!=0: sys.exit(f'falhou em {s}')
print('bootstrap concluido. Commite data/btc_daily_bitstamp.csv para o update diario ficar leve.')
