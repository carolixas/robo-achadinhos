"""Páginas públicas (GitHub Pages, pasta docs/):

  python paginas.py vitrine            -> docs/index.html: vitrine com os posts PUBLICADOS (mais recente primeiro)
                                          e os links de cada produto. É o link que vai na DM do "comenta QUERO"
                                          e pode ir na bio.
  python paginas.py previa <post_id>   -> docs/m/posts/<id>/index.html: prévia de um post da pauta (vídeo ou slides,
                                          legenda e produtos) para a Carol aprovar pelo celular.

Lê publicar/fila.json. Cada post pode ter "produtos": [{"nome","preco","loja","link"}].
"""
import html, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, "docs")
FILA = os.path.join(RAIZ, "publicar", "fila.json")
BASE = "https://carolixas.github.io/robo-achadinhos"
e = html.escape

CSS = """
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;background:#f6f1ea;color:#2a2622}
header{text-align:center;padding:28px 16px 8px}header h1{font-weight:500;font-size:22px;margin:0}header p{margin:6px 0 0;color:#7a6f64;font-size:14px}
main{max-width:560px;margin:0 auto;padding:8px 14px 40px}
.post{background:#fff;border-radius:18px;margin:16px 0;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.post h2{font-weight:500;font-size:17px;margin:0;padding:14px 16px 4px}.post .data{color:#9a8f84;font-size:12px;padding:0 16px 8px}
.midia img,.midia video{width:100%;display:block}.slides{display:flex;overflow-x:auto;scroll-snap-type:x mandatory}
.slides img{flex:0 0 100%;scroll-snap-align:start}
a.prod{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 16px;border-top:1px solid #f0ebe4;text-decoration:none;color:inherit}
a.prod span.n{font-size:15px}a.prod span.p{font-size:13px;color:#7a6f64;white-space:nowrap}a.prod b{color:#b0703a;font-weight:600}
.leg{white-space:pre-wrap;font-size:14px;padding:10px 16px;color:#4a433c;border-top:1px solid #f0ebe4}
.selo{display:inline-block;font-size:12px;padding:3px 8px;border-radius:99px;background:#efe6da;margin-left:6px}
footer{text-align:center;color:#a99e93;font-size:12px;padding:20px}
"""


def carregar():
    return json.load(open(FILA, encoding="utf-8")) if os.path.exists(FILA) else []


def lista_produtos(p):
    out = []
    for i, pr in enumerate(p.get("produtos", []), 1):
        out.append(f'<a class="prod" href="{e(pr["link"])}" target="_blank" rel="noopener">'
                   f'<span class="n">{i}. {e(pr["nome"])}</span>'
                   f'<span class="p"><b>{e(pr.get("preco", ""))}</b> · {e(pr.get("loja", ""))} ›</span></a>')
    return "".join(out)


def midia(p):
    if p["tipo"] == "reels":
        return f'<div class="midia"><video src="{e(p["video"])}" poster="{e(p.get("capa", ""))}" controls playsinline preload="none"></video></div>'
    return '<div class="midia slides">' + "".join(f'<img src="{e(u)}" loading="lazy">' for u in p.get("imagens", [])) + "</div>"


def pagina(titulo, corpo, og_img=""):
    og = f'<meta property="og:image" content="{e(og_img)}">' if og_img else ""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(titulo)}</title>
<meta property="og:title" content="{e(titulo)}">{og}<meta name="robots" content="noindex">
<style>{CSS}</style></head><body>{corpo}<footer>links de afiliado · preços podem mudar</footer></body></html>"""


def vitrine():
    fila = [p for p in carregar() if p.get("status") == "publicado"]
    fila.sort(key=lambda p: p.get("publicado_em", ""), reverse=True)
    blocos = []
    for p in fila[:30]:
        blocos.append(f'<section class="post" id="{e(p["id"])}"><h2>{e(p.get("tema", ""))}</h2>'
                      f'<div class="data">{e(p.get("publicado_em", "")[:10])}</div>{midia(p)}{lista_produtos(p)}</section>')
    corpo = ('<header><h1>achadinhos das carois 🛍️</h1><p>todos os links dos posts, do mais novo pro mais antigo</p></header>'
             f'<main>{"".join(blocos) or "<p>em breve ✨</p>"}</main>')
    capa = fila[0].get("capa") or (fila[0].get("imagens") or [""])[0] if fila else ""
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(pagina("achadinhos das carois 🛍️", corpo, capa))
    print("vitrine:", len(fila), "posts")


def previa(post_id):
    p = next(x for x in carregar() if x["id"] == post_id)
    pasta = os.path.join(DOCS, "m", "posts", post_id)
    os.makedirs(pasta, exist_ok=True)
    corpo = (f'<header><h1>prévia · {e(p["tipo"])}<span class="selo">{e(p.get("quando", "")[:16].replace("T", " "))}</span></h1>'
             f'<p>{e(p.get("tema", ""))}</p></header><main><section class="post">{midia(p)}'
             f'<div class="leg">{e(p.get("legenda", ""))}</div>{lista_produtos(p)}</section></main>')
    open(os.path.join(pasta, "index.html"), "w", encoding="utf-8").write(pagina("prévia " + post_id, corpo, p.get("capa", "")))
    print("prévia:", f"{BASE}/m/posts/{post_id}/")


if __name__ == "__main__":
    if sys.argv[1] == "vitrine":
        vitrine()
    else:
        previa(sys.argv[2])
