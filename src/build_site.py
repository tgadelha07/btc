"""build_site.py — embrulha o fragmento do app num documento HTML completo.

O arquivo app/index.html e um FRAGMENTO: a ferramenta Artifact injeta doctype,
head e body ao publicar. Para GitHub Pages (ou qualquer hospedagem estatica) o
arquivo precisa ser um documento inteiro. Este script gera site/index.html.
"""
import os, shutil
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frag=open(os.path.join(BASE,'app','index.html'),encoding='utf-8').read()
HEAD='''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Sistema quantitativo de DCA diario em Bitcoin.">
<style>
:root{color-scheme:light}
html,body{margin:0}
body{font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
</head>
<body>
'''
out=os.path.join(BASE,'site')
os.makedirs(out,exist_ok=True)
open(os.path.join(out,'index.html'),'w',encoding='utf-8').write(HEAD+frag+'\n</body>\n</html>\n')
shutil.copy(os.path.join(BASE,'app','data.js'), os.path.join(out,'data.js'))
open(os.path.join(out,'.nojekyll'),'w').write('')
print('site/index.html', f"{os.path.getsize(os.path.join(out,'index.html')):,} bytes")
print('site/data.js   ', f"{os.path.getsize(os.path.join(out,'data.js')):,} bytes")
