"""Gera Reels (1080x1920, com música) e carrossel (1080x1350) no estilo do @achadosdascarois.

Uso:
  python gerar.py reels  pauta.json      -> mp4 em "saida"
  python gerar.py carrossel pauta.json   -> slides jpg em "saida" (pasta)
  python gerar.py previa pauta.json      -> folha de prévia (jpg) com os quadros principais

pauta.json (caminhos relativos à pasta do json):
{
  "titulo": ["achados home decor", "da shopee :)"],
  "capa": {"imagem": "material/x.jpg", "fx": 0.5, "fy": 0.5},
  "itens": [
    {"imagem": "material/a.jpg", "miniatura": "material/a.jpg", "fx": 0.5, "fy": 0.5,
     "nome": "almofada redonda", "detalhe": "bouclê", "preco": "R$ 43",
     "nota": "4,9", "vendas": "10 mil vendidos", "loja": "Shopee", "a_partir": true}
  ],
  "musica": "../../musicas/zephiramusic-cute-lofi-613381.mp3",
  "saida": "reels.mp4"            (reels)  |  "saida": "slides"  (carrossel)
}
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, "fontes")
SERIF = os.path.join(FONTES, "CrimsonText-Regular.ttf")
SERIF_I = os.path.join(FONTES, "CrimsonText-Italic.ttf")
SANS_L = os.path.join(FONTES, "Inter-Light.otf")
SANS_M = os.path.join(FONTES, "Inter-Medium.otf")
HEROS = os.path.join(FONTES, "texgyreheros-regular.otf")
F = lambda p, s: ImageFont.truetype(p, s)
FPS = 30


# ---------- utilidades ----------
def abrir(base, p):
    return Image.open(os.path.join(base, p)).convert("RGB")


def caixa(src, W, H, z=1.0, fx=0.5, fy=0.5):
    sw, sh = src.size
    r = W / H
    if sw / sh > r:
        ch, cw = sh, sh * r
    else:
        cw, ch = sw, sw / r
    cw /= z; ch /= z
    x0 = max(0, min(sw - cw, fx * sw - cw / 2))
    y0 = max(0, min(sh - ch, fy * sh - ch / 2))
    return (x0, y0, x0 + cw, y0 + ch)


def texto_sombra(layer, xy, texto, fonte, fill=(255, 255, 255, 255), anchor="ma", blur=10, salpha=150, stroke=0):
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text(xy, texto, font=fonte, fill=(0, 0, 0, salpha), anchor=anchor,
                            stroke_width=stroke, stroke_fill=(0, 0, 0, salpha))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(layer).text(xy, texto, font=fonte, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=fill)


def degrade(layer, W, h, a, de_baixo=False):
    g = Image.new("L", (1, h))
    for y in range(h):
        k = (1 - y / h) ** 1.6
        g.putpixel((0, h - 1 - y if de_baixo else y), int(a * k))
    blk = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    blk.putalpha(g.resize((W, h)))
    layer.alpha_composite(blk, (0, layer.size[1] - h if de_baixo else 0))


def suave(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def com_alpha(img, a):
    if a >= 1:
        return img
    x = img.copy()
    x.putalpha(x.getchannel("A").point(lambda v: int(v * a)))
    return x


def titulo_layer(W, H, linhas, y0, tam=84, seta=True):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    degrade(L, W, int(H * 0.47), 175)
    f = F(HEROS, tam)
    y = y0
    for t in linhas:
        texto_sombra(L, (W // 2, y), t, f, blur=16, salpha=150, stroke=1)
        y += int(tam * 1.25)
    if seta:
        texto_sombra(L, (W // 2, y), "→", F(HEROS, int(tam * 0.76)), blur=12, salpha=150)
    return L


# ---------- REELS ----------
W, H = 1080, 1920


def item_layer(i, it):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    degrade(L, W, 760, 150)
    y = it.get("y_texto", 280)
    texto_sombra(L, (W // 2, y), f"{i:02d}", F(SANS_L, 34))
    texto_sombra(L, (W // 2, y + 52), it["nome"], F(SERIF, 92), salpha=190)
    if it.get("detalhe"):
        texto_sombra(L, (W // 2, y + 156), it["detalhe"], F(SERIF_I, 70), salpha=190)
    return L


def cartao(base, it):
    cw, chh = 560, 170
    C = Image.new("RGBA", (cw + 40, chh + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", C.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20, 24, 20 + cw, 24 + chh), 26, fill=(0, 0, 0, 90))
    C.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(C)
    d.rounded_rectangle((20, 20, 20 + cw, 20 + chh), 26, fill=(255, 255, 255, 240))
    t = abrir(base, it.get("miniatura") or it["imagem"])
    s = min(t.size)
    t = t.crop(((t.width - s) // 2, (t.height - s) // 2, (t.width + s) // 2, (t.height + s) // 2)).resize((134, 134), Image.LANCZOS)
    m = Image.new("L", (134, 134), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 133, 133), 18, fill=255)
    C.paste(t, (38, 38), m)
    loja = it.get("loja", "").lower()
    d.text((196, 46), f"{loja} · a partir de" if it.get("a_partir") else loja, font=F(SANS_L, 24), fill=(90, 90, 90))
    d.text((196, 80), it["preco"], font=F(SANS_M, 46), fill=(25, 25, 25))
    extra = "  ·  ".join(x for x in (f"★ {it['nota']}" if it.get("nota") else "", it.get("vendas", "")) if x)
    if extra:
        d.text((196, 140), extra, font=F(SANS_L, 22), fill=(160, 120, 40))
    return C


def fim_layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    L.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 120)))
    texto_sombra(L, (W // 2, 640), "comenta", F(SERIF_I, 96), blur=14, salpha=170)
    texto_sombra(L, (W // 2, 740), "QUERO", F(SERIF, 170), blur=14, salpha=170)
    texto_sombra(L, (W // 2, 960), "que eu te mando todos os links", F(SANS_L, 44), blur=10, salpha=170)
    return L


def quadros(src, dur, overlays, fx=0.5, fy=0.5, z0=1.0):
    n = int(round(dur * FPS))
    for f in range(n):
        z = z0 + 0.07 * (f / n)
        fr = src.resize((W, H), Image.BICUBIC, box=caixa(src, W, H, z, fx, fy)).convert("RGBA")
        for ov in overlays:
            ov(fr, f / FPS)
        yield fr


def ov_texto(L, t0=0.0, d=0.35):
    return lambda fr, t: fr.alpha_composite(com_alpha(L, suave((t - t0) / d)))


def ov_cartao(C, t0=0.35, d=0.35):
    def f(fr, t):
        a = suave((t - t0) / d)
        if a > 0:
            fr.alpha_composite(com_alpha(C, a), (50, int(1395 + 40 * (1 - a))))
    return f


def codificar(destino, frames, crf=21):
    tmp = destino + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", str(crf), "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    assert p.returncode == 0, destino
    os.replace(tmp, destino)


def reels(spec, base):
    tmpdir = tempfile.mkdtemp()
    partes = []
    capa = spec["capa"]
    src = abrir(base, capa["imagem"])
    caminho = os.path.join(tmpdir, "s00.mp4")
    codificar(caminho, quadros(src, 2.8, [ov_texto(titulo_layer(W, H, spec["titulo"], 140), 0.1, 0.4)], capa.get("fx", .5), capa.get("fy", .5)))
    partes.append(caminho)
    for i, it in enumerate(spec["itens"], 1):
        src = abrir(base, it["imagem"])
        caminho = os.path.join(tmpdir, f"s{i:02d}.mp4")
        codificar(caminho, quadros(src, 2.6, [ov_texto(item_layer(i, it)), ov_cartao(cartao(base, it))], it.get("fx", .5), it.get("fy", .5), it.get("zoom", 1.0)))
        partes.append(caminho)
    src = abrir(base, spec["itens"][0]["imagem"]).filter(ImageFilter.GaussianBlur(18))
    caminho = os.path.join(tmpdir, "s99.mp4")
    codificar(caminho, quadros(src, 3.2, [ov_texto(fim_layer(), 0.1, 0.4)]))
    partes.append(caminho)
    lista = os.path.join(tmpdir, "lista.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    video = os.path.join(tmpdir, "video.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video], check=True)
    dur = 2.8 + 2.6 * len(spec["itens"]) + 3.2
    saida = os.path.join(base, spec["saida"])
    musica = spec.get("musica")
    if musica:
        ini = float(spec.get("musica_inicio", 0))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ss", str(ini), "-i", os.path.join(base, musica),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-af", f"afade=t=in:d=0.6,afade=t=out:st={dur - 1.5:.2f}:d=1.5,volume=0.85",
                        "-t", f"{dur:.2f}", "-movflags", "+faststart", saida], check=True)
    else:
        os.replace(video, saida)
    # capa do Reels (primeiro quadro com o título, sem animação)
    capa_img = next(quadros(abrir(base, capa["imagem"]), 1 / FPS, [lambda fr, t: fr.alpha_composite(titulo_layer(W, H, spec["titulo"], 140))], capa.get("fx", .5), capa.get("fy", .5)))
    capa_img.convert("RGB").save(os.path.splitext(saida)[0] + "-capa.jpg", quality=90)
    print("ok", saida, f"{dur:.1f}s")


# ---------- CARROSSEL ----------
CW, CH = 1080, 1350


def slide_item(base, it):
    src = abrir(base, it["imagem"])
    fr = src.resize((CW, CH), Image.LANCZOS, box=caixa(src, CW, CH, it.get("zoom", 1.0), it.get("fx", .5), it.get("fy", .5))).convert("RGBA")
    L = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    degrade(L, CW, 420, 120, de_baixo=True)
    d = ImageDraw.Draw(L)
    x, y = 90, CH - 215
    d.line((x, y, x + 56, y), fill=(255, 255, 255, 230), width=2)
    nome = it["nome"] + (" " + it["detalhe"] if it.get("detalhe") else "")
    texto_sombra(L, (x, y + 26), nome, F(HEROS, 40), anchor="la", blur=8, salpha=120)
    texto_sombra(L, (x, y + 84), it["preco"], F(SERIF_I, 64), anchor="la", blur=8, salpha=120)
    fr.alpha_composite(L)
    return fr.convert("RGB")


def carrossel(spec, base):
    pasta = os.path.join(base, spec["saida"])
    os.makedirs(pasta, exist_ok=True)
    capa = spec["capa"]
    src = abrir(base, capa["imagem"])
    fr = src.resize((CW, CH), Image.LANCZOS, box=caixa(src, CW, CH, 1.0, capa.get("fx", .5), capa.get("fy", .5))).convert("RGBA")
    L = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    L.alpha_composite(Image.new("RGBA", (CW, CH), (0, 0, 0, 40)))
    f = F(HEROS, 66)
    y = CH // 2 - int(66 * 1.25 * len(spec["titulo"]) / 2)
    for t in spec["titulo"]:
        texto_sombra(L, (CW // 2, y), t, f, blur=16, salpha=160, stroke=1)
        y += int(66 * 1.25)
    texto_sombra(L, (CW // 2, y + 10), "→", F(HEROS, 50), blur=12, salpha=150)
    fr.alpha_composite(L)
    fr.convert("RGB").save(os.path.join(pasta, "01.jpg"), quality=90)
    for i, it in enumerate(spec["itens"], 2):
        slide_item(base, it).save(os.path.join(pasta, f"{i:02d}.jpg"), quality=90)
    print("ok", pasta, len(spec["itens"]) + 1, "slides")


def previa(spec, base):
    """Folha com capa + cada item (Reels) para conferir antes de renderizar."""
    shots = [next(quadros(abrir(base, spec["capa"]["imagem"]), 1 / FPS, [lambda fr, t: fr.alpha_composite(titulo_layer(W, H, spec["titulo"], 140))],
                          spec["capa"].get("fx", .5), spec["capa"].get("fy", .5)))]
    for i, it in enumerate(spec["itens"], 1):
        Lt, C = item_layer(i, it), cartao(base, it)
        shots.append(next(quadros(abrir(base, it["imagem"]), 1 / FPS, [lambda fr, t, Lt=Lt: fr.alpha_composite(Lt), lambda fr, t, C=C: fr.alpha_composite(C, (50, 1395))],
                                  it.get("fx", .5), it.get("fy", .5), it.get("zoom", 1.0))))
    cols = 5
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 270, rows * 480), "white")
    for k, s in enumerate(shots):
        sheet.paste(s.convert("RGB").resize((270, 480)), ((k % cols) * 270, (k // cols) * 480))
    out = os.path.join(base, "previa.jpg")
    sheet.save(out, quality=85)
    print("ok", out)


if __name__ == "__main__":
    modo, arq = sys.argv[1], sys.argv[2]
    spec = json.load(open(arq, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(arq))
    {"reels": reels, "carrossel": carrossel, "previa": previa}[modo](spec, base)
