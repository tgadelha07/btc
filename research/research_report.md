# research_report.md — BTC Dynamic DCA

Pesquisa concluída em 2026-09-13. Dados: preço Bitstamp BTC/USD 2012-01-01 →
2026-09-12 (5.369 dias, zero lacunas); on-chain Coin Metrics community
2010-07-18 → 2026-09-12. Preço de execução OHLC4, idêntico em todas as
estratégias. Defasagem de 1 dia para sinais de preço e 2 dias para on-chain.

---

## Resumo em uma frase

O DCA dinâmico funciona, o ganho vem quase inteiramente do **MVRV sozinho**, a
hipótese inicial do briefing é boa mas subótima porque combina indicadores
redundantes, e a fase de recuperação — testada e não assumida — **não se
sustenta**.

---

## As 12 respostas

### 1. O DCA dinâmico funcionou?

Sim, com uma qualificação importante sobre como isso é medido.

No backtest principal obrigatório (2021-01-01 → 2026-09-12, 2.081 dias), a regra
final acumulou **+22,36% mais BTC que o DCA uniforme de capital idêntico** e
reduziu o preço médio de aquisição em **18,27%**.

Em janelas móveis de 4 anos desde 2013 (119 janelas, uma a cada 30 dias), a
mediana da eficiência é **1,218** — ou seja, +21,8% de BTC com o mesmo capital — e
a estratégia vence em **82,4% das janelas**. A pior janela entregou 0,869
(−13,1%). O intervalo é largo: isso não é uma máquina de certezas.

No teste de permutação circular dentro de cada janela — o mesmo padrão de pesos
deslocado no tempo dentro da própria janela — a eficiência real fica no
**percentil 0,93** da distribuição nula, superando o próprio padrão embaralhado
em **100% das 60 janelas testadas**. Isso é a evidência de que o sinal está
alinhado a dias baratos, e não apenas concentrado no começo da série.

### 2. Quanto BTC adicional produziu usando o mesmo capital?

| Janela | BTC extra vs controle de capital igual |
|---|---|
| 2021-01-01 → 2026-09-12 (principal) | **+22,36%** |
| Mediana das janelas móveis de 4 anos | **+21,8%** |
| Mediana das janelas móveis de 5 anos | +17,0% |
| História completa 2013 → 2026, janela única | +3,29% |
| Treino 2013 → 2020, janela única | **−2,75%** |

A dispersão entre essas linhas não é ruído: é a armadilha metodológica descrita
na seção seguinte, e entendê-la é mais importante do que qualquer número isolado.

### 3. Quanto reduziu o preço médio?

**−18,27%** no período principal: US$34.764 contra US$42.536 do controle. Na
história completa a redução cai para 3,18%, pelo mesmo motivo estrutural.

### 4. Qual indicador isolado funcionou melhor?

**MVRV, com folga.** Comparação a capital equiparado (todos escalados para 1,31×
de capital, janelas móveis de 4 anos desde 2013):

| Modelo | Eficiência mediana | Vitórias | Rank de permutação |
|---|---|---|---|
| **MVRV sozinho** | **1,2178** | **82,4%** | **0,932** |
| H0 do briefing | 1,1290 | 73,9% | 0,822 |
| MVRV + MM200W | 1,1269 | 83,2% | 0,901 |
| RSI semanal sozinho | 1,1190 | 73,9% | 0,777 |
| Score completo, 5 indicadores | 1,1028 | 77,3% | 0,812 |
| Mayer sozinho | 1,0738 | 72,3% | 0,733 |

Sobre o Preço/MM200W há uma correção de método registrada na seção
"Reexame do Preço/MM200W" mais adiante: o número de 36,8% de vitórias que
constava na primeira versão deste relatório vinha de um teste injusto, porque a
MM200W só existe a partir de 31/10/2015 e as janelas começavam em 2013. Na
amostra justa ele tem sinal real, ainda que menor e mais caro que o do MVRV.

Hash Ribbons tem o comportamento oposto e interessante: efeito pequeno
(mediana 1,017) mas com correlação **negativa** (−0,24 a −0,37) com todos os
demais, ou seja, é o único que carrega informação de fato independente. Não foi
suficiente para entrar no modelo final, mas é o candidato mais honesto para uma
extensão futura.

### 5. Qual combinação funcionou melhor?

Nenhuma. Essa é a resposta desconfortável.

Varri **todos os 31 subconjuntos** de {MVRV, Mayer, MM200W, RSI, Hash Ribbons}
na arquitetura de Opportunity Score. A capital equiparado, **nenhuma combinação
supera o MVRV sozinho**. O modelo completo de 5 indicadores fica 9,4 pontos
percentuais de eficiência abaixo do modelo de 1 indicador.

O par MVRV + MM200W aparece em primeiro lugar quando o capital não é equiparado
(1,2329 contra 1,2164), mas consome 1,73× de capital contra 1,50×. Corrigido o
capital, ele perde.

### 6. Quais indicadores foram redundantes?

Três blocos, com evidência quantitativa:

**Bloco de valuation — redundância total.**
- NUPL ≡ MVRV: **correlação de Spearman 1,000**. Não é correlação alta, é
  identidade algébrica: NUPL = (MC − RC)/MC = 1 − 1/MVRV. NUPL não pode, em
  princípio, adicionar informação ao MVRV.
- Preço/Realized Price ↔ MVRV: 0,995 (φ dos sinais binários 0,968).
- MVRV Z-Score ↔ MVRV: 0,995.

Quatro dos indicadores candidatos do briefing são o mesmo indicador em unidades
diferentes. Tratá-los como "quatro confirmações independentes" seria contar a
mesma evidência quatro vezes — precisamente o que o item 5 proíbe.

**Bloco de momentum — redundância alta.**
- RSI semanal ↔ Mayer: **0,932**. E P(RSI semanal < 35 | Mayer < 0,8) = **0,90**.
  Quando o Mayer está deprimido, o RSI semanal está deprimido em 9 de cada 10 dias.

**Independente, porém fraco.** Hash Ribbons, como descrito acima.

### 7. Qual multiplicador máximo apresentou melhor equilíbrio?

Não existe um ótimo — existe uma **fronteira**, e a escolha nela é de preferência,
não de estatística. Escada MVRV 1,20/1,00/0,95/0,90:

| Perfil | Capital exigido | BTC extra (mediana 4a) | Vitórias | Pior janela | Pior 30 dias |
|---|---|---|---|---|---|
| 1× puro | 1,00× | 0,0% | — | 1,000 | 3.000 |
| Conservador 1,25/1,5/2/3 | 1,18× | +14,7% | 82,4% | 0,909 | 9.000 |
| Moderado 1,5/2/2,5/3 | 1,23× | +16,8% | 82,4% | 0,903 | 9.000 |
| **Agressivo 1,5/2/3/4** | **1,31×** | **+21,8%** | **82,4%** | **0,869** | **12.000** |
| Muito agressivo 2/3/4/5 | 1,46× | +28,0% | 82,4% | 0,832 | 15.000 |
| Extremo 2/4/6/8 | 1,74× | +38,7% | 82,4% | 0,761 | 24.000 |

A taxa de vitória é **constante em 82,4%** em toda a fronteira — escalar os
multiplicadores não muda a probabilidade de acerto, só a intensidade do acerto e
do erro. O retorno por unidade de capital extra cai monotonicamente: 0,78 no
extremo conservador contra 0,35 no extremo agressivo. Traduzindo: os primeiros
reais de aporte extra valem mais que os últimos.

O perfil **agressivo (1,5/2/3/4)** é a recomendação padrão — coincide com a
intuição original do briefing e fica no joelho da curva.

### 8. Vale manter aporte elevado durante a recuperação?

**Não.** Testei 4 gatilhos de recuperação × 5 durações (0/30/60/90/180 dias) × 5
multiplicadores (1,0 a 2,5×). O resultado é notavelmente plano: a eficiência
mediana permanece em **1,217–1,219 em todas as 25 combinações**, enquanto o
capital exigido sobe de 1,31× para até 1,62×.

A retenção de 180 dias a 2,5× exige 24% mais capital e devolve **zero** de
eficiência adicional. O retorno por unidade de capital cai de 0,70 para 0,35.

Há um efeito colateral pequeno e real: a taxa de vitória entre janelas sobe de
82,4% para 85,7%. Se o objetivo fosse minimizar a chance de ficar atrás do
controle, e não maximizar BTC, haveria um argumento fraco a favor de 30 dias a 2×
(custo de capital desprezível). Fora disso, a fase de recuperação é capital
gasto sem contrapartida. **Excluída do modelo final.**

Entre os gatilhos, o melhor foi "MVRV cruzando de volta acima de 1,0" (0,651 de
retorno por capital) e o pior foi "Hash Ribbon buy signal" (0,272) — este último
destrói mais valor por capital empregado do que qualquer outro testado.

### 9. Qual foi a estratégia vencedora de 2021 até hoje?

A escada de MVRV com cortes 1,20 / 1,00 / 0,95 / 0,90 e multiplicadores
1,5× / 2× / 3× / 4×.

| Métrica | A — DCA 100/dia | B — DCA dinâmico | C — uniforme, mesmo capital |
|---|---:|---:|---:|
| Capital investido | 208.100 | 255.300 | 255.300 |
| BTC acumulado | 4,892287 | **7,343864** | 6,001926 |
| Preço médio | 42.536 | **34.764** | 42.536 |
| Valor final | 378.023 | 567.455 | 463.764 |
| Lucro | 169.923 | 312.155 | 208.464 |
| ROI | 81,7% | 122,3% | 81,7% |
| Max drawdown | −50,5% | −50,7% | −50,5% |
| Maior aporte diário | 100 | 400 | 123 |
| **BTC adicional vs C** | — | **+22,36%** | — |
| **Melhora do preço médio** | — | **+18,27%** | — |

Distribuição dos dias: 85,3% em 1×, 6,0% em 1,5×, 1,5% em 2×, 3,1% em 3×,
4,0% em 4×. Capital nos piores 30 dias: 12.000 contra 3.000 do DCA fixo.

### 10. Ela também funcionou em períodos históricos anteriores?

**Depende inteiramente de como se mede — e essa é a descoberta metodológica mais
importante do estudo.**

Medida numa **janela única** de 2013 a 2020, a estratégia **perde**: eficiência
0,9725, ou −2,75% de BTC. Não escondo isso; o item 35 proíbe esconder.

A razão não é falha do indicador. Numa série exponencial, `E[1/p]` é dominado
pelos dias mais antigos: na janela 2013-2020, **64,9% de todo o "BTC por dólar"
disponível está em 2013**, quando o preço médio era US$187. E o MVRV **nunca**
esteve abaixo de 1 em 2013. Nenhum indicador de valuation poderia vencer aquela
janela — o prêmio inteiro estava num ano em que o sinal dizia "caro". Medir assim
avalia sobretudo o quanto a estratégia concentra capital no início, não a
qualidade do sinal.

Medida em **janelas móveis de horizonte realista**, que é como um investidor de
verdade vive o problema, o quadro se inverte e se estabiliza:

| Horizonte | Janelas | Eficiência mediana | Vitórias | Percentil 5 | Pior |
|---|---|---|---|---|---|
| 3 anos | 131 | 1,141 | 84,7% | 0,902 | 0,832 |
| 4 anos | 119 | 1,161 | 82,4% | 0,915 | 0,896 |
| 5 anos | 106 | 1,169 | 87,7% | 0,947 | 0,921 |

Funcionou na maioria dos períodos históricos, sim, mas não em todos, e o
desempenho é claramente melhor de 2018 em diante do que em 2013-2016.

### 11. Funcionou fora da amostra?

Sim. Walk-forward com 9 janelas: em cada ano os thresholds são escolhidos usando
**apenas** dados anteriores à data de decisão, e o desempenho é medido nos 2 anos
seguintes.

- Eficiência OOS média dos parâmetros otimizados: **1,1478**
- Eficiência OOS média de uma regra fixa ingênua (1,2/1,0/0,9/0,8): 1,0914
- A otimização superou a regra fixa em **7 das 9 janelas**, com vantagem média de +5,6 p.p.
- Única janela com perda: teste 2017-2019, eficiência 0,9633.
- Janela 2024-2026: eficiência exatamente 1,0000 — o sinal **nunca disparou**. O
  MVRV não desceu abaixo de 1,2 em nenhum dia de 2024 ou 2025.

O achado mais tranquilizador do walk-forward é a **estabilidade dos parâmetros**:
o otimizador escolheu 1,2/1,0/0,95/0,90 em seis janelas consecutivas e
1,2/1,1/1,0/0,90 nas três últimas. Não há saltos erráticos, que seriam a
assinatura de overfitting.

A análise de sensibilidade confirma. Perturbando os thresholds em ±0,05 e ±0,10
(24 combinações), a eficiência por unidade de capital extra varia entre 0,556 e
0,784 (desvio-padrão 0,071) e a **taxa de vitória nunca sai da faixa 82%–86%**.
A superfície é suave e monotônica, não um pico estreito.

### 12. Qual regra devemos colocar no aplicativo?

O aplicativo publicado oferece **dois motores** com chave nas Configurações. A
recomendação técnica continua sendo a escada de MVRV; o score composto está
disponível para quem prefere a leitura agregada dos quatro indicadores, com o
custo medido e exibido na própria tela.

**Motor 1 — BTC Dynamic DCA v1.0 (recomendado):** um único indicador, cinco
estados, sem fase de recuperação.

```
Opportunity Score = f(MVRV), linear por partes:
   MVRV ≥ 2,00              →   0
   MVRV 2,00 → 1,50         →   0 → 25
   MVRV 1,50 → 1,20         →  25 → 50
   MVRV 1,20 → 1,00         →  50 → 70
   MVRV 1,00 → 0,95         →  70 → 80
   MVRV 0,95 → 0,90         →  80 → 90
   MVRV 0,90 → 0,70         →  90 → 100
   MVRV ≤ 0,70              → 100
```

| Estado | Score | MVRV | Multiplicador (perfil agressivo) |
|---|---|---|---|
| NORMAL | < 50 | ≥ 1,20 | 1,0× |
| ATRATIVO | 50–70 | 1,00–1,20 | 1,5× |
| MUITO ATRATIVO | 70–80 | 0,95–1,00 | 2,0× |
| CAPITULAÇÃO | 80–90 | 0,90–0,95 | 3,0× |
| EXTREMO HISTÓRICO | ≥ 90 | < 0,90 | 4,0× |

O score é uma reexpressão monotônica do MVRV construída para que os cortes
50/70/80/90 sejam **exatamente** os cortes validados de MVRV. Score e regra são o
mesmo objeto em duas unidades — não há um segundo modelo escondido atrás do número.

**Motor 2 — Score composto:** média ponderada das baratezas point-in-time de
MVRV (45), Preço/MM200W (30), RSI semanal (15) e Mayer (10), com estados em
70 / 76 / 82 / 88. Calibrado por grid restrito e validado em walk-forward, como
descrito na seção anterior. Custa cerca de 8 pontos de eficiência a capital
igualado e entrega em troca uma leitura mais rica e um sinal mais suave.

Em ambos os motores, todos os indicadores aparecem na tela com uma barra de
força de compra — fraca, moderada, forte ou muito forte — construída sobre o
percentil histórico point-in-time. Os que ficam fora do índice (NUPL, Realized
Price, MVRV Z-Score, Hash Ribbons) são marcados como tal, com o motivo escrito
no próprio cartão.

---

## O score composto que foi para o aplicativo

Por decisão de produto, o aplicativo passou a oferecer **dois motores**, com chave
nas Configurações. O segundo é um índice composto dos quatro principais
indicadores, calibrado — não arbitrado.

**Calibração.** Grid de 11.990 modelos (1.199 vetores de peso × 10 conjuntos de
corte), com a restrição de que os quatro indicadores tenham peso ≥ 1, avaliados
em janelas móveis de 4 anos desde 2013. Registro honesto: **deixado livre, o
otimizador zera Mayer e RSI** e converge para MVRV sozinho ou MVRV + MM200W. Os
pesos abaixo são o melhor modelo *sujeito à exigência* de que os quatro participem.

| | MVRV | MM200W | RSI | Mayer | Eficiência | Capital |
|---|---|---|---|---|---|---|
| Ótimo sem restrição | 100 | 0 | 0 | 0 | 1,2377 | 1,600× |
| Média dos 50 melhores com restrição | 47,1 | 28,4 | 14,5 | 10,0 | 1,2232 | 1,591× |
| **Pesos adotados** | **45** | **30** | **15** | **10** | **1,2173** | **1,555×** |

Desvio-padrão dos pesos relativos entre os 50 melhores: 0,087 / 0,091 / 0,052 /
0,029. Região estável, não um pico estreito. Cortes: **70 / 76 / 82 / 88**.

**Walk-forward.** Pesos e cortes reescolhidos a cada janela usando só dados
anteriores, medidos nos 2 anos seguintes: OOS médio **1,1753** para o ótimo por
janela contra **1,1647** para os pesos fixos adotados — diferença de 0,01, ou
seja, fixar não custa praticamente nada. Os cortes 70/76/82/88 foram escolhidos
em 6 das 8 janelas. Uma única janela ficou abaixo do empate (teste 2024-2026,
0,9954).

**O que o composto custa.** Nos respectivos níveis naturais de capital os dois
motores praticamente empatam em eficiência mediana (1,2173 do composto contra
1,2169 da escada de MVRV), mas o composto chega lá consumindo 1,555× de capital
contra 1,310×. **Igualando o capital em 1,31×, a escada de MVRV entrega 1,2178
contra 1,1399 do composto** — cerca de 8 pontos percentuais de eficiência é o
preço da leitura mais rica. Em troca, o composto tem a mesma taxa de acerto
(82,4%) e pior janela ligeiramente melhor (0,873 contra 0,869): é um sinal mais
suave, que erra menos feio e acerta menos alto.

No período principal 2021→hoje, o composto entrega +23,88% de BTC contra +22,36%
da escada — mas com 1,53× de capital contra 1,23×. A tabela "Os dois motores,
lado a lado" no aplicativo mostra isso em cada configuração.

## Reexame do Preço/MM200W — correção de um teste injusto

A primeira versão deste relatório afirmou que o Preço/MM200W isolado era
"indistinguível de moeda ao ar", com 36,8% de vitórias. Essa conclusão estava
contaminada: a MM200W exige 1.400 dias de preço e só passa a existir em
**31/10/2015**, mas as janelas móveis começavam em 2013. Em toda janela iniciada
antes de 2016, o indicador ficava inerte nos primeiros anos e a estratégia
simplesmente comprava 1× — o que produz eficiência exatamente 1,000 e arrasta a
mediana e a taxa de vitória para baixo. Na amostra justa, iniciando em 2015-11:

| Escada 1,2/1,0/0,9/0,8 → 1,5/2/3/4× | Janelas de 5 anos | Janelas de 4 anos |
|---|---|---|
| MM200W, início 2013 (injusto) | 0,9969 · 36,8% | 1,0000 · 49,6% |
| MM200W, início 2015-11 (justo) | 1,0080 · 54,2% | **1,0468 · 69,0%** |
| MVRV, início 2015-11 (mesma amostra) | 1,1169 · 84,7% | **1,1458 · 78,6%** |

O indicador tem sinal. Mas na mesma amostra o MVRV entrega **1,146 consumindo
1,21× de capital**, contra **1,047 consumindo 1,36×** da MM200W — mais resultado
com menos dinheiro imobilizado.

### Comparação direta com `BTC/MM200W < 1,2`

Amostra comum 2015-11-01 → 2026-09-12 (3.969 dias). Os dois sinais são
correlacionados (φ = 0,626) e disparam em frequências muito diferentes: MVRV<1,20
em **12,8%** dos dias, MM200W<1,20 em **19,3%**.

No threshold nominal 1,2 e multiplicador 2×, empatam — a MM200W chega a ganhar em
janelas de 3 anos (1,0896 contra 1,0803) e no período principal 2021→hoje (1,1389
contra 1,1215). Mas essa vantagem é de **volume de capital, não de seleção**: ela
dispara em 30,8% dos dias de 2021→hoje contra 14,7% do MVRV. Igualando a
comparação, a ordem se inverte:

| Comparação | MVRV | BTC/MM200W |
|---|---|---|
| Frequência igualada em 12,8% dos dias | **1,0914 · 77,4% vitórias** | 1,0179 · 65,5% |
| Frequência igualada em 19,3% dos dias | **1,0979 · 81,0%** | 1,0801 · 70,2% |
| Capital igualado em 1,20× | **1,0987 · 77,4%** | 1,0748 · 70,2% |
| 2021 → hoje, capital igualado | 1,1317 | 1,1304 |

A MM200W não é pior em tudo. Ela tem **pior janela melhor** (0,956 contra 0,934)
e **rank de permutação mais alto** (0,940 contra 0,892): é um sinal mais suave, que
erra menos feio e acerta menos alto. Nos poucos dias em que os dois discordam, os
dias marcados só pela MM200W foram em média 11% mais baratos que os marcados só
pelo MVRV — mas são 82 dias contra 340, amostra pequena demais para sustentar peso.

Por período, o MVRV vence 2015-2018, 2019-2020 e 2021-2023; a MM200W vence
2024→hoje e o período principal 2021→hoje no threshold nominal. A vantagem
recente da MM200W tem explicação mecânica: seu denominador é a média de 200
semanas do próprio preço, que sobe com atraso depois de um ciclo de alta, de modo
que "abaixo de 1,2× a MM200W" fica progressivamente mais fácil de satisfazer à
medida que a série amadurece. O denominador do MVRV é o custo de aquisição
efetivo da rede, que se atualiza com o comportamento real dos detentores.

### Combinar os dois não ajuda

| Regra | Eficiência | Vitórias | Capital |
|---|---|---|---|
| MVRV<1,2 sozinho | **1,0914** | **77,4%** | 1,182× |
| MVRV **ou** MM200W | 1,0949 | 71,4% | 1,230× |
| MVRV **e** MM200W (confirmação) | 1,0796 | 77,4% | 1,182× |
| MVRV que a MM200W **não** confirma | 1,0002 | 69,0% | 1,013× |

Exigir confirmação da MM200W **piora** o MVRV com exatamente o mesmo capital
(1,0914 → 1,0796). A união melhora 0,0035 de eficiência ao custo de 4,8 pontos
percentuais de capital extra e de 6 pontos de taxa de vitória. Nenhum dos dois
arranjos justifica o segundo indicador.

**Veredito:** o MVRV continua sendo o melhor indicador isolado — mais eficiência
por unidade de capital e taxa de vitória consistentemente mais alta entre janelas
—, mas a afirmação anterior de que a MM200W "não tem sinal" estava errada e foi
produzida por um teste mal especificado.

## O que não funcionou — registro explícito (item 35)

| Hipótese testada | Resultado |
|---|---|
| Escada H0 do briefing com 6 estados | Funciona (+13,3% em 2021-2026) mas perde para MVRV sozinho a capital igual. Os degraus 2× e 4× **nunca dispararam** no período principal |
| Adicionar Mayer ao MVRV | Piora: 1,2178 → 1,1572 |
| Adicionar RSI ao MVRV | Piora: 1,2178 → 1,1832 |
| Adicionar Hash Ribbons a qualquer modelo | Piora todos os subconjuntos sem exceção |
| Modelo completo de 5 indicadores | 1,1028 — 14º lugar entre 31 subconjuntos |
| Preço/MM200W isolado | Tem sinal real (69,0% de vitórias em janelas de 4 anos na amostra justa), mas entrega menos que o MVRV consumindo mais capital: 1,047 a 1,36× contra 1,146 a 1,21×. Ver "Reexame do Preço/MM200W" |
| Preço/MM200W como filtro de confirmação do MVRV | Piora o MVRV a capital idêntico: 1,0914 → 1,0796 |
| Fase de recuperação, 25 variantes | Eficiência inalterada, capital até +24% |
| Função contínua `(c/MVRV)^β` | Comparável à escada, nunca superior a capital igual. Escada preferida por simplicidade |
| MVRV por percentil em vez de nível | Eficiência levemente maior (1,181 vs 1,159) mas rank de permutação menor (0,897 vs 0,950) e depende de janela expanding instável nos primeiros anos. Nível preferido |
| Janela única de 14 anos como métrica | Rejeitada por dominância do ponto de partida |

## Riscos que o backtest não captura

O modelo tem apenas **três ciclos** de Bitcoin para aprender. Todos terminaram em
recuperação. A estratégia concentra capital exatamente nos momentos de maior
estresse — é por construção a mais exposta ao cenário em que a recuperação não
vem. O max drawdown de 83,3% na história completa é o que isso significa na prática.

O capital extra precisa existir e estar parado. Nos piores 30 dias de 2021-2026 o
modelo exigiu 12.000 contra 3.000 do DCA fixo — quatro vezes mais, num momento em
que o portfólio estava em queda de 50%. O custo de oportunidade desse capital não
está contabilizado, e a disciplina emocional necessária também não.

E o mais banal dos riscos: em 12 de setembro de 2026 o MVRV está em **1,45**,
score **30**, estado **NORMAL**, multiplicador **1×**. O modelo passou 2024 e 2025
inteiros sem disparar. Ele é desenhado para ficar quieto na maior parte do tempo —
85,3% dos dias no período principal — e essa espera é a parte difícil.
