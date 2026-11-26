import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import api
testes = [
 ("link", "mutation{generateShortLink(input:{originUrl:\"https://shopee.com.br/product/544374309/58270107598\",subIds:[\"canal\"]}){shortLink}}", None),
 ("busca1", "query{productOfferV2(keyword:\"vaso\",limit:3){nodes{itemId productName price}}}", None),
 ("busca2", "query{productOfferV2(keyword:\"vaso\",sortType:2,page:1,limit:3){nodes{itemId productName priceMin ratingStar sales imageUrl offerLink}}}", None),
 ("busca3", "query{productOfferV2(limit:3){nodes{itemId productName}}}", None),
 ("shopee", "query{shopeeOfferV2(keyword:\"casa\",limit:2){nodes{offerName commissionRate}}}", None),
]
for nome, q, v in testes:
    try:
        print(nome, "OK", str(api.gql(q, v))[:400])
    except Exception as e:
        print(nome, "ERRO", str(e)[:300])
