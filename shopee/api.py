"""API oficial de afiliados da Shopee (GraphQL). Roda no GitHub Actions.
Segredos: SHOPEE_APP_ID e SHOPEE_SECRET (GitHub > Settings > Secrets).
Uso:
  python shopee/api.py buscar "vaso decorativo" [limite]
  python shopee/api.py link https://shopee.com.br/product/<shopid>/<itemid> [...]
"""
import hashlib, json, os, sys, time, urllib.request

URL = "https://open-api.affiliate.shopee.com.br/graphql"
APP = os.environ.get("SHOPEE_APP_ID", "").strip()
SEG = os.environ.get("SHOPEE_SECRET", "").strip()


def gql(query, variables=None):
    corpo = json.dumps({"query": query, "variables": variables or {}}, separators=(",", ":"))
    ts = str(int(time.time()))
    assinatura = hashlib.sha256((APP + ts + corpo + SEG).encode()).hexdigest()
    req = urllib.request.Request(URL, data=corpo.encode(), method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={APP}, Timestamp={ts}, Signature={assinatura}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
    if resp.get("errors"):
        raise RuntimeError(json.dumps(resp["errors"], ensure_ascii=False)[:500])
    return resp["data"]


def buscar(termo, limite=20):
    # a API não aceita variáveis nem alguns campos (ex.: price) nesta consulta: valores vão direto no texto
    k = json.dumps(termo, ensure_ascii=False)
    campos = ["itemId shopId productName priceMin ratingStar sales imageUrl offerLink commissionRate",
              "itemId productName priceMin ratingStar sales imageUrl offerLink"]
    erro = None
    for c in campos:
        q = "query{productOfferV2(keyword:%s,sortType:2,page:1,limit:%d){nodes{%s}}}" % (k, int(limite), c)
        try:
            return gql(q)["productOfferV2"]["nodes"]
        except RuntimeError as e:
            erro = e
    raise erro


def link(url):
    q = 'mutation{generateShortLink(input:{originUrl:%s,subIds:["canal"]}){shortLink}}' % json.dumps(url)
    return gql(q)["generateShortLink"]["shortLink"]


if __name__ == "__main__":
    if not APP or not SEG:
        print("Faltam os segredos SHOPEE_APP_ID / SHOPEE_SECRET"); sys.exit(1)
    if sys.argv[1] == "buscar":
        for n in buscar(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10):
            print(f"{n['productName'][:60]} | R$ {n.get('priceMin')} | {n.get('ratingStar')} | {n.get('sales')} vendidos | {n.get('offerLink')}")
    elif sys.argv[1] == "link":
        for u in sys.argv[2:]:
            print(u, "->", link(u))
