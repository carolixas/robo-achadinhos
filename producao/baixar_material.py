"""Baixa as fotos pedidas em producao/material_pedido.json -> producao/material/<post>/<arquivo>.
Formato: {"<post_id>": {"a.jpg": "https://...", ...}}. Roda no GitHub Actions (o container não alcança as CDNs)."""
import io, json, os, urllib.request
from PIL import Image
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ped = json.load(open(os.path.join(RAIZ, "producao", "material_pedido.json")))
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/131 Safari/537.36"}
for post, fotos in ped.items():
    pasta = os.path.join(RAIZ, "producao", "material", post)
    os.makedirs(pasta, exist_ok=True)
    for nome, url in fotos.items():
        destino = os.path.join(pasta, nome)
        if os.path.exists(destino):
            continue
        try:
            dados = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
            img = Image.open(io.BytesIO(dados)).convert("RGB")
            if max(img.size) > 2000:
                img.thumbnail((2000, 2000))
            img.save(destino, quality=92)
            print("ok", post, nome, img.size)
        except Exception as e:
            print("ERRO", post, nome, e)
