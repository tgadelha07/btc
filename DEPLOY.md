# Como colocar no ar

Leva uns 10 minutos e nao custa nada. Voce nao precisa de Railway, Render, Heroku
nem de qualquer servico de servidor: o painel e um arquivo HTML estatico.

## 1. Criar o repositorio

No GitHub, "New repository". Pode ser privado — o Pages funciona em repositorio
privado em contas Pro; se a sua for gratuita, deixe publico.

Depois, no seu computador, dentro da pasta descompactada:

```bash
git init
git add .
git commit -m "BTC Dynamic DCA"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/btc-dynamic-dca.git
git push -u origin main
```

## 2. Ligar o GitHub Pages

No repositorio: **Settings -> Pages**. Em "Build and deployment", mude
**Source** de "Deploy from a branch" para **GitHub Actions**. So isso. Nao mexa
em mais nada nessa tela.

## 3. Rodar o workflow uma primeira vez

Aba **Actions** -> "Atualizacao diaria" -> botao **Run workflow**.

Na primeira execucao o GitHub pode pedir para voce habilitar os workflows do
repositorio; e um botao verde no topo da aba Actions.

Ao terminar, o endereco aparece no proprio job "publicar" e tambem em
Settings -> Pages. Fica assim:

```
https://SEU-USUARIO.github.io/btc-dynamic-dca/
```

## 4. Pronto

A partir daqui o workflow roda sozinho todo dia as 07:30 UTC (04:30 em
Brasilia), baixa os dados novos, regenera o painel e republica. Se nenhum dado
mudou, ele nao commita nada.

Para mudar o horario, edite o `cron` em `.github/workflows/daily.yml`. O campo e
sempre em UTC.

---

## Perguntas que costumam aparecer

**E se eu quiser um dominio proprio?** Settings -> Pages -> Custom domain, e um
registro CNAME no seu provedor de DNS apontando para `SEU-USUARIO.github.io`.

**Da para usar Netlify ou Vercel em vez do Pages?** Da. Aponte o build para a
pasta `site/` e deixe o comando de build vazio. Mas nesse caso a atualizacao
diaria continua sendo do GitHub Actions — os dois servicos tambem nao rodam
Python em cron no plano gratuito.

**Por que nao Railway?** Railway mantem um contêiner de pe. Aqui nao ha processo
para manter: o navegador baixa dois arquivos e faz todo o resto. Voce pagaria
por um servidor ocioso servindo arquivos estaticos, e ainda assim precisaria de
um agendador separado para atualizar os dados.

**Quanto o Actions consome?** O job baixa cerca de 5 MB e roda em menos de um
minuto. Em repositorio publico o Actions e ilimitado; em privado, o plano
gratuito da 2.000 minutos por mes — isso aqui usa uns 30.

**O painel some se o workflow falhar?** Nao. O site continua no ar com os
ultimos dados que deram certo; so para de envelhecer... digo, so para de
rejuvenescer. A aba Actions mostra a falha.

**As preferencias (aporte-base, perfil, moeda) ficam salvas?** No GitHub Pages
elas ficam no navegador de cada pessoa, via localStorage. A sincronizacao entre
dispositivos so existe na versao publicada como Artifact no Claude, que tem
banco proprio.
