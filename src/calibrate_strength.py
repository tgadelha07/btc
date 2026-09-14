"""calibrate_strength.py — calibra as faixas de "forca de compra" por indicador.

O erro que isto corrige: rotular a barra pelo percentil bruto faz "compra forte"
acender em ~40% de todos os dias da historia e, no caso do MVRV, acender bem
antes do ponto em que o modelo validado comeca a agir (MVRV < 1,20 = percentil
18,2). O rotulo dizia uma coisa e o multiplicador dizia outra.

Aqui as faixas sao definidas pelo LIFT MEDIDO: para cada decil de percentil do
indicador, mede-se quanto BTC por dolar aquele dia comprava contra a media da
janela (mediana entre janelas moveis de 4 anos). O rotulo entao significa a
mesma coisa em todos os indicadores:

    muito forte : lift >= 1,45
    forte       : lift >= 1,15
    moderada    : lift >= 1,00
    fraca       : lift  < 1,00

Regra de monotonicidade: depois que um decil cai abaixo de 1,00, os decis
seguintes ficam em "fraca" mesmo que algum suba por ruido.
"""
import sys, os, json; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, analyze as an

LIFT_LIMITS = [1.00, 1.15, 1.45]     # moderada, forte, muito forte
LABELS = ['fraca','moderada','forte','muito forte']
INDS = {'mvrv':'pct_mvrv','p_ma200w':'pct_p_ma200w','rsi_weekly':'pct_rsi_weekly',
        'mayer':'pct_mayer','price_to_rp':'pct_price_to_rp','mvrv_zscore':'pct_mvrv_zscore',
        'nupl':'pct_mvrv'}
H, STEP, START = 1460, 30, '2013-01-01'

def main():
    P, S = an.PANEL, an.SIG
    d = P[P.index >= pd.Timestamp(START)]
    inv = 1.0/d['ohlc4'].to_numpy(float)

    def lift(mask):
        vals=[]
        for s0 in range(0, len(d)-H+1, STEP):
            iv=inv[s0:s0+H]; m=mask[s0:s0+H]
            if m.sum() < 20: continue
            vals.append(iv[m].mean()/iv.mean())
        return float(np.median(vals)) if len(vals) >= 20 else np.nan

    out={}
    for key, pc in INDS.items():
        p=(100*S[pc]).reindex(d.index).to_numpy(float)
        deciles=[lift((p>=i*10)&(p<(i+1)*10)) for i in range(10)]
        # rotulo de cada decil, com a regra de monotonicidade
        labels=[]; travado=False
        for L in deciles:
            if travado or not (L==L) or L < LIFT_LIMITS[0]:
                travado = travado or (L==L and L < LIFT_LIMITS[0])
                labels.append(0); continue
            k=0
            for lim in LIFT_LIMITS:
                if L >= lim: k+=1
            labels.append(k)
        # converte para limites de percentil: ate onde vai cada rotulo
        bounds={}
        for lvl in (3,2,1):
            top=0
            for i,l in enumerate(labels):
                if l>=lvl: top=(i+1)*10
                else: break
            bounds[LABELS[lvl]]=top           # 0 = o indicador nunca alcanca esse rotulo
        out[key]=dict(deciles=[None if L!=L else round(L,3) for L in deciles],
                      labels=labels,
                      p_muito_forte=bounds['muito forte'],
                      p_forte=bounds['forte'],
                      p_moderada=bounds['moderada'])
    path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'out','strength_bands.json')
    json.dump(out, open(path,'w'), indent=1)
    print('out/strength_bands.json gravado\n')
    for k,v in out.items():
        print(f"  {k:<14} muito forte ate p{v['p_muito_forte']:<3} | forte ate p{v['p_forte']:<3} | moderada ate p{v['p_moderada']:<3}")
    return out

if __name__ == '__main__':
    main()
