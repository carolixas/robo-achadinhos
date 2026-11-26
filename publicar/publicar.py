"""Publica no Instagram (@achadosdascarois) os posts APROVADOS da fila.

Fila: publicar/fila.json  ->  lista de posts:
  {"id": "2026-11-27-reels-1", "tipo": "reels" | "carrossel",
   "quando": "2026-11-27T12:30:00-03:00", "status": "aprovado",
   "legenda": "...", "video": "<url mp4>", "capa": "<url jpg>",       (reels)
   "imagens": ["<url jpg>", ...]}                                       (carrossel)
Só publica status == "aprovado" com "quando" já passado. Depois grava
status "publicado", media_id, link e publicado_em. Erros ficam em "erro".
Modo teste: TESTE=1 cria os containers mas NÃO publica.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

API = "https://graph.facebook.com/v23.0"
IG_ID = os.environ.get("IG_USER_ID", "17841400158670151")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
TESTE = os.environ.get("TESTE") == "1"
FILA = os.path.join(os.path.dirname(__file__), "fila.json")
# Reels saem como "teste" (Testes de Reels): primeiro só para quem não segue;
# se for bem nas primeiras ~72 h, o Instagram compartilha sozinho com os seguidores
# e no perfil (SS_PERFORMANCE). Um post pode desligar com "teste_reels": false.
TESTE_REELS = True
TRIAL = json.dumps({"graduation_strategy": "SS_PERFORMANCE"})


def chamar(metodo, caminho, **params):
    params["access_token"] = TOKEN
    dados = urllib.parse.urlencode(params).encode()
    url = f"{API}/{caminho}"
    if metodo == "GET":
        req = urllib.request.Request(url + "?" + dados.decode())
    else:
        req = urllib.request.Request(url, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace").replace(TOKEN, "***")
        raise RuntimeError(f"{caminho}: HTTP {e.code} {corpo[:400]}")


def esperar_pronto(cid, limite=600):
    t0 = time.time()
    while time.time() - t0 < limite:
        st = chamar("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {cid}: {st}")
        time.sleep(10)
    raise RuntimeError(f"container {cid} não ficou pronto em {limite}s")


def criar(post):
    if post["tipo"] == "reels":
        p = dict(media_type="REELS", video_url=post["video"], caption=post["legenda"])
        if post.get("capa"):
            p["cover_url"] = post["capa"]
        if post.get("teste_reels", TESTE_REELS):
            try:
                cid = chamar("POST", f"{IG_ID}/media", trial_params=TRIAL, **p)["id"]
                post["teste_reels"] = True
            except RuntimeError as e:
                # conta ainda não pode usar Testes de Reels: publica como Reels normal
                post["teste_reels"] = False
                post["teste_reels_obs"] = "Instagram recusou o modo teste: " + str(e)[:200]
                print("  modo teste recusado, indo como Reels normal:", e)
                cid = chamar("POST", f"{IG_ID}/media", share_to_feed="true", **p)["id"]
        else:
            cid = chamar("POST", f"{IG_ID}/media", share_to_feed="true", **p)["id"]
        esperar_pronto(cid)
        return cid
    if post["tipo"] == "carrossel":
        filhos = []
        for url in post["imagens"][:10]:
            filhos.append(chamar("POST", f"{IG_ID}/media", image_url=url, is_carousel_item="true")["id"])
        for f in filhos:
            esperar_pronto(f, 180)
        cid = chamar("POST", f"{IG_ID}/media", media_type="CAROUSEL", children=",".join(filhos), caption=post["legenda"])["id"]
        esperar_pronto(cid, 180)
        return cid
    raise RuntimeError(f"tipo desconhecido: {post['tipo']}")


def main():
    if not TOKEN:
        print("Falta o secret IG_ACCESS_TOKEN."); sys.exit(1)
    fila = json.load(open(FILA, encoding="utf-8")) if os.path.exists(FILA) else []
    agora = datetime.now(timezone(timedelta(hours=-3)))
    mudou = False
    for post in fila:
        if post.get("status") != "aprovado":
            continue
        if datetime.fromisoformat(post["quando"]) > agora:
            continue
        print(f"→ {post['id']} ({post['tipo']})")
        try:
            cid = criar(post)
            if TESTE:
                print(f"  TESTE: container {cid} pronto, não publicado"); continue
            mid = chamar("POST", f"{IG_ID}/media_publish", creation_id=cid)["id"]
            info = chamar("GET", mid, fields="permalink")
            post.update(status="publicado", media_id=mid, link=info.get("permalink"),
                        publicado_em=agora.isoformat(timespec="minutes"))
            print(f"  publicado: {post['link']}")
        except Exception as e:
            post["erro"] = str(e)[:500]
            post["tentativas"] = post.get("tentativas", 0) + 1
            if post["tentativas"] >= 3:
                post["status"] = "erro"
            print(f"  ERRO: {e}")
        mudou = True
    if mudou and not TESTE:
        json.dump(fila, open(FILA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    pend = [p["id"] for p in fila if p.get("status") == "aprovado"]
    print(f"Na fila aprovados aguardando horário: {pend}")


if __name__ == "__main__":
    main()
