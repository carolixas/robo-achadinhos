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
    q = """query($k:String,$l:Int){productOfferV2(keyword:$k,sortType:2,page:1,limit:$l){
      nodes{itemId shopId productName price priceMin ratingStar sales imageUrl productLink offerLink commissionRate}}}"""
    return gql(q, {"k": termo, "l": limite})["productOfferV2"]["nodes"]


def link(url):
    q = """mutation($u:String!){generateShortLink(input:{originUrl:$u,subIds:["canal"]}){shortLink}}"""
    return gql(q, {"u": url})["generateShortLink"]["shortLink"]


if __name__ == "__main__":
    if not APP or not SEG:
        print("Faltam os segredos SHOPEE_APP_ID / SHOPEE_SECRET"); sys.exit(1)
    if sys.argv[1] == "buscar":
        for n in buscar(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10):
            print(f"{n['productName'][:60]} | R$ {n.get('priceMin') or n.get('price')} | {n.get('ratingStar')} | {n.get('sales')} vendidos | {n.get('offerLink')}")
    elif sys.argv[1] == "link":
        for u in sys.argv[2:]:
            print(u, "->", link(u))
