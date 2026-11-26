"""Responde o "comenta QUERO" dos posts publicados pelo robô (substitui o ManyChat nos posts novos).

Para cada post da fila com status "publicado" (últimos 7 dias):
  - lê os comentários;
  - se o comentário pede os links (quero, eu quero, queroo...), responde o comentário em público
    e manda os links daquele post na DM (resposta privada ao comentário);
  - guarda o id do comentário em publicar/respondidos.json para nunca responder duas vezes.
Modo teste: TESTE=1 só lista o que faria, sem responder nada.
"""
import json, os, random, re, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from publicar import chamar, IG_ID, TOKEN, FILA  # noqa: E402

TESTE = os.environ.get("TESTE") == "1"
FEITOS = os.path.join(os.path.dirname(__file__), "respondidos.json")
CANAL = "https://whatsapp.com/channel/0029Vb9O6P31dAwCV1mRV714"
VITRINE = "https://carolixas.github.io/robo-achadinhos/"
EU = "achadosdascarois"
PEDIDO = re.compile(r"\b(eu\s+)?quer+o+\b|\bquer\b|\bqro\b|\blink", re.I)
RESPOSTAS = ["te mandei no direct 🤍", "corre no direct que os links tão lá ✨", "enviado! olha sua DM 🤌🏻"]
NUM = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def montar_dm(post):
    linhas = ["oii! que bom que você gostou 🤍", ""]
    tema = post.get("tema", "").strip()
    linhas += [f"aqui estão os links dos achadinhos{(' de ' + tema.lower()) if tema else ''} ✨", ""]
    for i, p in enumerate(post.get("produtos", [])[:10]):
        linhas += [f"{NUM[i]} {p['nome']} · {p.get('preco', '')}".rstrip(" ·"), f"👉 {p['link']}", ""]
    linhas += [f"💚 entra no canal pra receber achadinhos todo dia: {CANAL}"]
    texto = "\n".join(linhas)
    if len(texto) > 990:  # limite da DM do Instagram (1000)
        texto = ("oii! que bom que você gostou 🤍\n\naqui estão todos os links desse post ✨\n"
                 f"👉 {VITRINE}#{post['id']}\n\n💚 canal de achadinhos: {CANAL}")
    return texto


def main():
    if not TOKEN:
        print("Falta o secret IG_ACCESS_TOKEN."); sys.exit(1)
    fila = json.load(open(FILA, encoding="utf-8")) if os.path.exists(FILA) else []
    feitos = set(json.load(open(FEITOS))) if os.path.exists(FEITOS) else set()
    limite = datetime.now(timezone.utc) - timedelta(days=7)
    novos = 0
    for post in fila:
        if post.get("status") != "publicado" or not post.get("media_id") or not post.get("produtos"):
            continue
        quando = datetime.fromisoformat(post.get("publicado_em") or post["quando"])
        if quando < limite:
            continue
        url = f"{post['media_id']}/comments"
        params = dict(fields="id,text,username,timestamp", limit=50)
        while True:
            r = chamar("GET", url, **params)
            for c in r.get("data", []):
                if c["id"] in feitos or c.get("username", "").lower() == EU:
                    continue
                if not PEDIDO.search(c.get("text", "")):
                    continue
                print(f"→ {post['id']}: @{c.get('username')} disse {c.get('text')!r}")
                if TESTE:
                    continue
                try:
                    chamar("POST", f"{IG_ID}/messages",
                           recipient=json.dumps({"comment_id": c["id"]}),
                           message=json.dumps({"text": montar_dm(post)}, ensure_ascii=False))
                    chamar("POST", f"{c['id']}/replies", message=random.choice(RESPOSTAS))
                    feitos.add(c["id"]); novos += 1
                except Exception as e:
                    print(f"  ERRO: {e}")
            nxt = r.get("paging", {}).get("cursors", {}).get("after") if r.get("paging", {}).get("next") else None
            if not nxt:
                break
            params["after"] = nxt
    if novos and not TESTE:
        json.dump(sorted(feitos), open(FEITOS, "w"), indent=0)
    print(f"Respondidos agora: {novos}")


if __name__ == "__main__":
    main()
