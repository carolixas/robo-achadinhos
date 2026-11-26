"""Robô de ofertas na nuvem do @achadosdascarois.

Roda no GitHub Actions uma vez por dia. Busca produtos de casa/decor no
AliExpress pela API oficial de afiliados (preço em reais e link de afiliado
prontos), filtra pelos critérios do perfil, tira o que já foi sugerido antes e
grava o resultado em sugestoes/ultimas.json (e uma cópia com a data).

As chaves NUNCA ficam no código: vêm dos "secrets" do repositório
(ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET, ALIEXPRESS_TRACKING_ID).
Só usa a biblioteca padrão do Python.
"""

import datetime as dt
import hashlib
import hmac
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CONFIG = RAIZ / "config.json"
HISTORICO = RAIZ / "dados" / "ja_sugeridos.json"
PASTA_SAIDA = RAIZ / "sugestoes"

ALI_URL = "https://api-sg.aliexpress.com/sync"
CAMPOS = (
    "product_id,product_title,target_sale_price,target_original_price,discount,"
    "evaluate_rate,lastest_volume,commission_rate,product_main_image_url,"
    "product_small_image_urls,promotion_link,shop_name,product_detail_url"
)


def carregar_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", str(t).lower())
                   if unicodedata.category(c) != "Mn")


def num(v, padrao=0.0):
    try:
        return float(str(v).replace("%", "").replace(",", ".").strip())
    except (TypeError, ValueError):
        return padrao


def assinar(params, segredo):
    base = "".join(f"{k}{params[k]}" for k in sorted(params))
    return hmac.new(segredo.encode(), base.encode(), hashlib.sha256).hexdigest().upper()


def buscar(chave, segredo, tracking, palavra, pagina=1, limite=50):
    params = {
        "app_key": chave,
        "timestamp": str(int(time.time() * 1000)),
        "sign_method": "sha256",
        "method": "aliexpress.affiliate.product.query",
        "keywords": palavra,
        "page_no": str(pagina),
        "page_size": str(limite),
        "sort": "LAST_VOLUME_DESC",
        "target_currency": "BRL",
        "target_language": "PT",
        "ship_to_country": "BR",
        "tracking_id": tracking,
        "fields": CAMPOS,
    }
    params["sign"] = assinar(params, segredo)
    req = urllib.request.Request(
        ALI_URL,
        data=urllib.parse.urlencode(params).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        dados = json.loads(r.read().decode())
    if "error_response" in dados:
        raise RuntimeError(dados["error_response"].get("msg") or str(dados["error_response"]))
    resp = dados.get("aliexpress_affiliate_product_query_response", {}).get("resp_result", {})
    if str(resp.get("resp_code", "200")) != "200":
        raise RuntimeError(resp.get("resp_msg") or "erro desconhecido")
    return ((resp.get("result") or {}).get("products") or {}).get("product") or []


def normalizar(n, palavra):
    preco = num(n.get("target_sale_price"))
    preco_de = num(n.get("target_original_price")) or None
    taxa = num(n.get("commission_rate")) / 100
    pid = str(n.get("product_id"))
    imagens = (n.get("product_small_image_urls") or {}).get("string") or []
    return {
        "id": f"aliexpress:{pid}",
        "loja": "AliExpress",
        "busca": palavra,
        "nome": n.get("product_title") or "",
        "preco": round(preco, 2),
        "preco_de": round(preco_de, 2) if preco_de and preco_de > preco else None,
        "desconto": int(num(n.get("discount"))),
        # o AliExpress dá % de avaliações positivas; 96% vira nota 4,8
        "nota": round(num(n.get("evaluate_rate")) / 20, 2),
        "vendas": int(num(n.get("lastest_volume"))),
        "comissao_pct": round(taxa * 100, 1),
        "imagem": n.get("product_main_image_url") or "",
        "imagens": imagens[:6],
        "link_afiliado": n.get("promotion_link") or "",
        "link_produto": f"https://pt.aliexpress.com/item/{pid}.html",
        "loja_vendedor": n.get("shop_name") or "",
    }


def passa(p, cfg):
    if p["preco"] <= 0 or not p["link_afiliado"]:
        return False
    if not (cfg["preco_minimo"] <= p["preco"] <= cfg["preco_maximo"]):
        return False
    if p["nota"] < cfg["nota_minima"] or p["vendas"] < cfg["vendas_minimas"]:
        return False
    nome = sem_acento(p["nome"])
    return not any(sem_acento(x) in nome for x in cfg["palavras_proibidas"])


def pontuar(p):
    return (
        (p["nota"] - 4) * 25
        + math.log10(p["vendas"] + 1) * 6
        + min(p["comissao_pct"], 20) * 0.8
        + min(p["desconto"], 70) * 0.15
    )


def main():
    chave = os.environ.get("ALIEXPRESS_APP_KEY", "").strip()
    segredo = os.environ.get("ALIEXPRESS_APP_SECRET", "").strip()
    tracking = os.environ.get("ALIEXPRESS_TRACKING_ID", "").strip() or "default"
    if not chave or not segredo:
        print("Faltam os secrets ALIEXPRESS_APP_KEY / ALIEXPRESS_APP_SECRET no repositório.")
        sys.exit(1)
    # diagnóstico sem revelar valores: só o formato
    print(f"App Key: {len(chave)} caracteres, só números: {chave.isdigit()} | Secret: {len(segredo)} caracteres")

    cfg = carregar_config()
    historico = {}
    if HISTORICO.exists():
        historico = json.loads(HISTORICO.read_text(encoding="utf-8"))

    hoje = dt.date.today()
    dia = hoje.toordinal()
    buscas = cfg["buscas"]
    n = min(cfg["buscas_por_rodada"], len(buscas))
    inicio = (dia * n) % len(buscas)
    da_vez = [buscas[(inicio + i) % len(buscas)] for i in range(n)]

    vistos, candidatos, erros = set(), [], []
    for palavra in da_vez:
        try:
            for bruto in buscar(chave, segredo, tracking, palavra):
                p = normalizar(bruto, palavra)
                if p["id"] in vistos or p["id"] in historico:
                    continue
                vistos.add(p["id"])
                if passa(p, cfg):
                    p["pontos"] = round(pontuar(p), 1)
                    candidatos.append(p)
        except Exception as e:  # noqa: BLE001 - uma busca com erro não derruba as outras
            erros.append(f"{palavra}: {e}")
        time.sleep(1)

    candidatos.sort(key=lambda p: p["pontos"], reverse=True)
    # no máximo 2 produtos da mesma busca, pra variar
    escolhidos, por_busca = [], {}
    for p in candidatos:
        if por_busca.get(p["busca"], 0) >= 2:
            continue
        escolhidos.append(p)
        por_busca[p["busca"]] = por_busca.get(p["busca"], 0) + 1
        if len(escolhidos) >= cfg["sugestoes_por_rodada"]:
            break

    saida = {
        "gerado_em": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "buscas": da_vez,
        "erros": erros,
        "produtos": escolhidos,
    }
    PASTA_SAIDA.mkdir(exist_ok=True)
    texto = json.dumps(saida, ensure_ascii=False, indent=2)
    (PASTA_SAIDA / "ultimas.json").write_text(texto, encoding="utf-8")
    (PASTA_SAIDA / f"{hoje.isoformat()}.json").write_text(texto, encoding="utf-8")

    for p in escolhidos:
        historico[p["id"]] = hoje.isoformat()
    HISTORICO.parent.mkdir(exist_ok=True)
    HISTORICO.write_text(json.dumps(historico, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(escolhidos)} sugestões de {len(candidatos)} candidatos. Buscas: {', '.join(da_vez)}")
    for e in erros:
        print("ERRO:", e)
    if erros and not escolhidos:
        sys.exit(1)


if __name__ == "__main__":
    main()
