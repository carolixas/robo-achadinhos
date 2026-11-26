"""Baixa as fotos das páginas do canal (docs/m/<slug>.jpg, 800x800) listadas em producao/fotos_canal.json.
Roda no GitHub Actions (o container do Claude não alcança as CDNs das lojas)."""
import io, json, os, urllib.request
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lista = json.load(open(os.path.join(RAIZ, "producao", "fotos_canal.json")))
for slug, url in lista.items():
    destino = os.path.join(RAIZ, "docs", "m", slug + ".jpg")
    if os.path.exists(destino):
        continue
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/131 Safari/537.36"})
    try:
        img = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
    except Exception as e:
        print("ERRO", slug, e)
        continue
    w, h = img.size
    lado = min(w, h)
    img = img.crop(((w - lado) // 2, (h - lado) // 2, (w - lado) // 2 + lado, (h - lado) // 2 + lado)).resize((800, 800), Image.LANCZOS)
    img.save(destino, quality=88)
    print("ok", slug)
