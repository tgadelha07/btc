"""final_model.py — os dois motores de sinal do BTC Dynamic DCA.

FONTE A — 'mvrv' (validada): escada de MVRV 1,20/1,00/0,95/0,90. Vencedora do
  criterio do item 33: 1,2178 de eficiencia mediana a 1,31x de capital.
FONTE B — 'composto': score ponderado de MVRV(45) + MM200W(30) + RSI(15) +
  Mayer(10) sobre percentis point-in-time, cortes 70/76/82/88. Calibrada por
  grid restrito (os quatro com peso >= 1) e validada em walk-forward: OOS medio
  1,1647 com pesos fixos contra 1,1753 do otimo por janela. A capital igualado
  em 1,31x rende 1,1399 contra 1,2178 da escada de MVRV — sinal mais suave,
  mesma taxa de acerto (82,4%), pior janela ligeiramente melhor.
"""
import numpy as np, pandas as pd

# ---- fonte A: escada de MVRV
KNOTS = [(2.00, 0.0), (1.50, 25.0), (1.20, 50.0), (1.00, 70.0),
         (0.95, 80.0), (0.90, 90.0), (0.70, 100.0)]
CUTS_MVRV = [50.0, 70.0, 80.0, 90.0]
MVRV_BOUNDS = [1.20, 1.00, 0.95, 0.90]

# ---- fonte B: score composto
WEIGHTS = {'MVRV': 45, 'MM200W': 30, 'RSI': 15, 'Mayer': 10}
CUTS_COMP = [70.0, 76.0, 82.0, 88.0]

PROFILE_MULTS = {'conservador': (1.25,1.5,2.0,3.0), 'moderado': (1.5,2.0,2.5,3.0),
                 'agressivo': (1.5,2.0,3.0,4.0), 'muito agressivo': (2.0,3.0,4.0,5.0)}
STATES = ['NORMAL','ATRATIVO','MUITO ATRATIVO','CAPITULACAO','EXTREMO HISTORICO']

def opportunity_score(mvrv):
    x = np.asarray(mvrv, dtype=float)
    xs = np.array([k[0] for k in KNOTS]); ys = np.array([k[1] for k in KNOTS])
    out = np.interp(x, xs[::-1], ys[::-1])
    out = np.where(x >= KNOTS[0][0], 0.0, out)
    out = np.where(x <= KNOTS[-1][0], 100.0, out)
    return pd.Series(out, index=mvrv.index if hasattr(mvrv,'index') else None)

def composite_score(sig):
    """sig: frame com as colunas pct_* ja defasadas. Pesos renormalizados sobre
       os componentes disponiveis no dia, para a MM200W (so desde 31/10/2015)
       nunca bloquear o score."""
    comp = pd.DataFrame({'MVRV':1-sig['pct_mvrv'], 'MM200W':1-sig['pct_p_ma200w'],
                         'RSI':1-sig['pct_rsi_weekly'], 'Mayer':1-sig['pct_mayer']})
    w = pd.Series(WEIGHTS, dtype=float)
    wm = comp.notna().mul(w, axis=1)
    return ((comp.fillna(0)*wm).sum(axis=1)/wm.sum(axis=1).replace(0,np.nan))*100

def multiplier(score, profile='agressivo', source='mvrv'):
    cuts = CUTS_MVRV if source=='mvrv' else CUTS_COMP
    mults = PROFILE_MULTS[profile]
    m = pd.Series(1.0, index=score.index)
    for c, mu in zip(cuts, mults): m[(score >= c).fillna(False)] = mu
    return m

def state_index(score, source='mvrv'):
    cuts = CUTS_MVRV if source=='mvrv' else CUTS_COMP
    i = pd.Series(0, index=score.index)
    for j,c in enumerate(cuts): i[(score>=c).fillna(False)] = j+1
    return i

# ---- forca de compra por indicador (a partir da barateza point-in-time)
STRENGTH_CUTS = [0.35, 0.60, 0.80]
STRENGTH = ['fraca','moderada','forte','muito forte']
def strength_index(cheapness):
    k = 0
    for c in STRENGTH_CUTS:
        if cheapness >= c: k += 1
    return k
