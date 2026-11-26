"""Teste seguro: cria um container de carrossel com 2 fotos e confere se ficou pronto.
NÃO publica nada (não chama media_publish). Containers não publicados expiram sozinhos em 24 h."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import publicar as p

base = "https://carolixas.github.io/robo-achadinhos/m/"
filhos = [p.chamar("POST", f"{p.IG_ID}/media", image_url=base + n, is_carousel_item="true")["id"]
          for n in ("puff-pe-palito.jpg", "almofada-boucle.jpg")]
for f in filhos:
    p.esperar_pronto(f, 180)
cid = p.chamar("POST", f"{p.IG_ID}/media", media_type="CAROUSEL", children=",".join(filhos), caption="teste")["id"]
p.esperar_pronto(cid, 180)
print("OK: container de carrossel pronto (não publicado):", cid)
