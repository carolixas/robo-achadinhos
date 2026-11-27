# Roteiro da produção diária — @achadosdascarois

**Chrome: use SEMPRE o do PC Windows** (list_connected_browsers → select_browser no osPlatform "Windows"). O MacBook não é mais usado.

Meta do dia: **2 Reels + 1 carrossel**, prontos para a Carol aprovar na aba **Pauta** da planilha.
Depois de aprovados, o GitHub publica sozinho no horário (fila `publicar/fila.json`).

Horários padrão (Brasília): **Reels A 12:30 · Carrossel 18:00 · Reels B 20:30**.
Id dos posts: `AAAA-MM-DD-reels-a`, `AAAA-MM-DD-carrossel`, `AAAA-MM-DD-reels-b`.

## Regras fixas
- Só LEIA as lojas: nunca comprar, carrinho, cupom, seguir loja, login, aceitar termos. Cookies: recusar não essenciais.
- Tela de login/captcha/verificação: não resolver; pular aquela loja e avisar no fim.
- Nunca inventar preço, nota, vendas ou link. Só o que leu na página.
- Nunca ler nem mostrar `chaves-e-ajustes.txt`.
- Trabalhe em abas próprias e feche as que abrir.

## 1. Planejar
1. Planilha "Central Achadinhos das Carois" (Sheets, id `c09e65e4-99af-4eee-84a0-4e8c1cac6e04`): chame o guide do conector Claude Docs com `["topic.sheets"]` e siga-o. Leia as abas **Pauta**, **Posts** e **Produtos**.
2. Se a Pauta já tem os 3 posts de hoje, pare ("pauta de hoje já existe").
3. Escolha 3 temas que não apareceram nos últimos 7 dias (Posts/Pauta). Ideias: home decor, cantinho do café, quarto aconchegante, banheiro spa, cozinha bonita, mesa posta, organização bonita, home office, luminárias, vasos e plantas, decor de Natal (até 25/12), presentes até R$ 50 (dezembro), varanda, quarto de bebê/criança (raramente).
4. Lojas: **Reels A = Shopee**; **Reels B = Amazon nos dias pares, Mercado Livre nos ímpares**; **Carrossel = a loja que sobrou** (ou misto). AliExpress só se faltar produto.
5. 6 produtos por post (mínimo 5). Nada repetido da aba Produtos nem dentro do dia.

## 2. Achar os produtos (Chrome da Carol)
Critérios: estética clean/aconchegante/"parece caro" (neutros, madeira, vidro, cerâmica, bouclê, palha, linho), preço até ~R$ 150 (ideal até R$ 60), nota ≥ 4,5, muitas vendas/avaliações (de preferência 500+), **foto bonita de ambiente** (vira o fundo do vídeo). Nada utilitário/feio, marca famosa, personagem ou réplica.
- **Shopee (preferido: API oficial, sem captcha)**: dispare `gh api -X POST repos/carolixas/robo-achadinhos/actions/workflows/shopee-busca.yml/dispatches -f ref=main -f "inputs[termos]=termo 1, termo 2, termo 3"`, espere ~1 min, `git pull` e leia `producao/shopee_busca.json` (por termo: itemId, shopId, productName, priceMin, ratingStar, sales, imageUrl, offerLink = **link de afiliado pronto**, commissionRate). Foto: imageUrl. Não precisa do passo 3 pra Shopee. Pra montar uma grade de fotos, abra as imageUrl numa aba do Chrome (innerHTML) como nas outras lojas.
- **Shopee (reserva, se a API falhar)**: abra https://shopee.com.br e, de dentro da página, rode
  `fetch('/api/v4/search/search_items?by=sales&keyword=<termo>&limit=60&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2').then(r=>r.json())`.
  Em `items[].item_basic`: `name`, `price/100000` (R$), `item_rating.rating_star`, `historical_sold`, `image`, `images[]`, `shopid`, `itemid`.
  Foto: `https://down-br.img.susercontent.com/file/<hash>`. Link: `https://shopee.com.br/product/<shopid>/<itemid>`.
  Se o fetch for bloqueado (erro 90309999), espere 1 min e tente outro termo; ou leia https://shopee.com.br/search?keyword=<termo>&sortBy=sales.
- **Amazon**: https://www.amazon.com.br/s?k=<termo> → página do produto. Preço `#corePrice_feature_div .a-offscreen`, nota `#acrPopover[title]`, avaliações `#acrCustomerReviewText`, foto `#landingImage[data-old-hires]` (e outras em `#altImages`). ASIN no link `/dp/<ASIN>`.
- **Mercado Livre**: https://lista.mercadolivre.com.br/<termo-com-hifens> → página do produto. Preço, nota, vendidos e `meta[property="og:image"]`.

## 3. Links de afiliado (gerar só para os escolhidos)
- **Shopee**: https://affiliate.shopee.com.br/offer/custom_link → cole até 5 links de produto (um por linha) na caixa de texto (form_input), clique em "Obter link" e copie os `https://s.shopee.com.br/...`. ID de afiliado: 18315280280.
- **Amazon** (tag `achadosd09778-20` (conta de Associados do perfil de achadinhos; carolixas-20 é a conta antiga, não usar)): numa aba da amazon.com.br rode
  `fetch('/associates/sitestripe/getShortUrl?longUrl='+encodeURIComponent('https://www.amazon.com.br/dp/<ASIN>?tag=achadosd09778-20')+'&marketplaceId=526970').then(r=>r.json())` → `shortUrl` (`https://amzn.to/...`).
  O Chrome precisa estar logado na amazon.com.br com a conta de Associados achadosd09778-20 (a da Carol); deslogado, o encurtador devolve uma página HTML em vez de JSON. Nesse caso use o link longo `https://www.amazon.com.br/dp/<ASIN>?tag=achadosd09778-20` (funciona igual) e avise a Carol pra logar.
- **Mercado Livre**: na página do produto (logada), use a barra de afiliados do topo ("Compartilhar"/"Gerar link") e copie o `https://meli.la/...`.
- Se não conseguir o link de afiliado de um produto, troque o produto.

## 4. Baixar as fotos
Para cada post, numa aba de qualquer loja, monte um zip **sem compressão** em JavaScript com as fotos (fetch de cada URL → Uint8Array; zip "store" com CRC32) e baixe com `<a download="material-<post_id>.zip">`. As CDNs (susercontent, media-amazon, mlstatic) permitem fetch.
(Desde 27/11 tudo roda no **PC Windows** da Carol, não no Mac.) Jeito preferido, sem zip: liste as URLs em `producao/material_pedido.json` (`{"<post_id>": {"<arquivo>.jpg": "<url>", ...}}`), dispare `gh api -X POST repos/carolixas/robo-achadinhos/actions/workflows/material.yml/dispatches -f ref=main`, espere ~1 min, `git pull` e as fotos estarão em `producao/material/<post_id>/`.
Use 1 foto de ambiente por produto como fundo e, se tiver, a foto do produto em fundo claro como miniatura.

## 5. Montar (no container)
1. `add_repo` carolixas/robo-achadinhos com acesso **push**, clone, e use `producao/gerar.py`.
2. Música: `device_stage_files` de 1 música da pasta `musicas/` dentro da pasta conectada do PC (`Documentos\Achadinhos Carolixas\musicas`; o caminho exato vem de `get_device_info`). Varie a música entre os posts; não repita a do dia anterior se der.
3. Escreva `pauta.json` (formato no topo de `gerar.py`). Título curto e minúsculo, no estilo "achados home decor / da shopee :)", "cantinho do café / que parece caro :)". Itens: `nome` (2–3 palavras), `detalhe` (1–2 palavras), `preco` "R$ 43", `nota` "4,9", `vendas` "10 mil vendidos" (Amazon: "2 mil avaliações"), `loja`.
4. Rode `python producao/gerar.py previa pauta.json`, **abra a previa.jpg com Read** e ajuste `fx`/`fy`/`zoom`/`y_texto` se o texto cobrir o produto ou o recorte estiver ruim. Repita até ficar bom.
5. Reels: `python producao/gerar.py reels pauta.json` (gera `reels.mp4` e `reels-capa.jpg`). Carrossel: mesmo json com `"saida": "slides"` → `python producao/gerar.py carrossel car.json`. Confira 2–3 quadros/slides com Read.

## 6. Publicar a mídia e a fila (repo)
1. Copie para `docs/m/posts/<post_id>/`: Reels → `reels.mp4` e `capa.jpg`; carrossel → `01.jpg…NN.jpg`.
2. Para cada produto **Shopee**, crie também a página de prévia do canal: `docs/m/<slug>.jpg` (foto 800×800) e `docs/l/<slug>/index.html` (copie o modelo de `docs/l/puff-pe-palito/index.html` trocando título, descrição, imagem e link).
3. Acrescente o post em `publicar/fila.json`:
   ```json
   {"id": "<post_id>", "tipo": "reels"|"carrossel", "tema": "<tema>", "quando": "AAAA-MM-DDT12:30:00-03:00",
    "status": "aguardando",
    "legenda": "comenta QUERO pra receber todos os links 🤌🏻😮‍💨",
    "video": "https://carolixas.github.io/robo-achadinhos/m/posts/<id>/reels.mp4",
    "capa": "https://carolixas.github.io/robo-achadinhos/m/posts/<id>/capa.jpg",
    "imagens": ["https://carolixas.github.io/robo-achadinhos/m/posts/<id>/01.jpg", "..."],
    "pasta_mac": "posts/NN-<slug>",
    "produtos": [{"nome": "almofada redonda bouclê", "preco": "R$ 43", "preco_num": 43.0, "loja": "Shopee",
                  "link": "<link de afiliado>", "link_canal": "<página docs/l/... só Shopee>"}]}
   ```
   (carrossel não tem video/capa; Reels não tem imagens). Legenda: a linha do QUERO; pode ter 1 frase curta antes, sem hashtags em excesso (no máx. 3).
4. `python producao/paginas.py previa <post_id>` para cada post. Commit e push. Espere ~1 min e confira que `https://carolixas.github.io/robo-achadinhos/m/posts/<id>/` abre (no Chrome).

## 7. Guardar no PC e avisar
1. (Opcional) `device_commit_files`: vídeo/slides e um `legenda-e-links.txt` (legenda + lista numerada de produtos com links) em `posts/NN-<slug>/` dentro da pasta conectada do PC. Se falhar, siga sem isso.
2. Aba **Pauta**: uma linha por post — A id · B "Reels"/"Carrossel" · C tema + loja · D horário ({"dateTime": ...}) · E `{"markdown":"[ver prévia](https://carolixas.github.io/robo-achadinhos/m/posts/<id>/)"}` · F "Aguardando" · G "Aguardando aprovação". Não mexa em outras linhas.
3. **Agende a produção de amanhã** (a produção roda na conversa do PC com a Carol, porque tarefas com pastas fecham em 5 s): `send_later` para amanhã 08:13 `[America/Sao_Paulo]`, nome "Produção diária: 2 Reels + 1 carrossel", initiation `human_schedule`, com a mesma mensagem que te acordou hoje. Confira com `list_triggers` que ficou 1 só.
4. Mensagem final (vira notificação): "Pauta de amanhã/hoje pronta 👇" + 1 linha por post (tipo · tema · horário) + "Aprova na aba Pauta (tem prévia de cada um) que eu publico sozinha no horário." Se algo falhou, diga o quê.

## 8. Resultados dos links (todo dia, depois de avisar a pauta)
Só LER os painéis (nada de sacar, aceitar termos ou mudar configuração). Login/captcha: anotar "precisa login" e seguir.
1. Shopee: https://affiliate.shopee.com.br/report/click_report (cliques de ontem; "Total de N") e /report/conversion_report (pedidos, valor, comissão).
2. Mercado Livre: https://www.mercadolivre.com.br/afiliados/dashboard (cliques, ordens, vendas e ganho estimados).
3. Amazon: https://associados.amazon.com.br/p/reporting/earnings (cliques, pedidos, ganhos; conta achadosd09778-20; escolher "Ontem" se der).
4. AliExpress: https://portals.aliexpress.com/affiportals/web/home.htm (cliques, pedidos pagos, ganhos em US$; 2 dias de atraso).
Na aba **Resultados** da planilha: 4 linhas novas abaixo da última (A data de hoje · B loja · C período lido, ex. "ontem 26/11" · D cliques · E pedidos · F vendas R$ · G comissão R$ · H observação). Nunca apagar linhas antigas; não duplicar se já houver linhas de hoje. Nunca inventar número.
Na mensagem da pauta, acrescente 1 linha: "Ontem: X cliques · Y vendas · R$ Z de comissão" (se houve venda, comece com 💸).

## 9. Repor a fila do canal do WhatsApp (todo dia)
O canal posta 1 achadinho a cada 30 min (≈32/dia) misturando categorias: **casa 40% · beleza 30% · eletrônico 20% · pet 10%** (coluna E da aba Produtos: "canal beleza", "canal eletrônico", "canal pet"; qualquer outro valor = casa).
Conte quantos produtos de cada categoria ainda não foram enviados (H vazio). Se alguma categoria tiver menos de 2 dias de estoque (casa < 26, beleza < 20, eletrônico < 13, pet < 7), acrescente produtos novos dessa categoria no fim da aba Produtos (A nome · B loja · C preço · D link de afiliado · E categoria · F "Na fila" · G hoje · I página com foto se Shopee).
- Shopee pela API (`shopee-busca.yml`): o `offerLink` já é o link de afiliado; pra ter foto no canal crie `docs/l/<slug>/index.html` (modelo `docs/l/puff-pe-palito/`) e acrescente `"<slug>": "<imageUrl>"` em `producao/fotos_canal.json` (o workflow baixa a foto sozinho).
- Critérios: nota ≥ 4,6, vendas/avaliações ≥ 1.000, preço justo, foto bonita. **Nada de réplica** (ex.: fone genérico com logo JBL, "AirPods"/"Pods Pro" falsos), nada de marca usada sem ser a loja oficial em eletrônico. Beleza: marcas conhecidas ou loja oficial; nada de promessa de resultado.
- Eletrônico bom na Amazon: Echo/Alexa, Fire TV, Kindle, soundcore, Xiaomi Redmi Buds, lâmpada smart. Pet: areia biodegradável, fonte/bebedouro, arranhador, brinquedos interativos.

## Lições do 1º dia (26/11)
- **Shopee pode mostrar captcha** depois de ~10 buscas seguidas pela API (página `/verify/captcha`). Não resolva: espere, faça no máximo 5 buscas por rodada com 2 s entre elas, ou use outra loja nesse dia.
- **Amazon funciona muito bem por fetch** de dentro de uma aba da amazon.com.br: `fetch('/s?k=<termo>')` → DOMParser → `div[data-component-type="s-search-result"]` (ASIN em `data-asin`, preço `.a-price .a-offscreen`, nota no `aria-label` "de 5 estrelas", avaliações no link `#customerReviews`, patrocinado `.puis-sponsored-label-text`). Fotos grandes: na página `/dp/<ASIN>` os `"hiRes":"https://..."` do HTML.
- **Para escolher fotos**, monte uma grade de miniaturas numeradas na própria aba (innerHTML) e tire 1 screenshot — muito mais rápido que abrir produto por produto.
- **Mercado Livre**: o fetch da busca não traz os cards (são montados por JS). Abra a busca na aba e leia os `.poly-card` da página já carregada (nota e vendidos em `.poly-component__review-compacted`, ex. "4.9 | +500 vendidos"; anúncios têm link `click1.mercadolivre`).
- **Foto de produto em fundo branco**: no carrossel o gerador já detecta e centraliza no branco com texto escuro. No Reels, gere antes um fundo 1080×1920 branco com o produto centralizado (≈960 px) e use como `imagem`.
- Evite foto com comida/objetos fora do tema (ex.: cesto com pão num post de quarto) — a Carol reprova.
- Não repita a mesma foto como capa e como item; se precisar, use `zoom`/`fy` diferentes.

---

# Sincronização (tarefa de hora em hora, na nuvem)
1. Leia a aba Pauta e `publicar/fila.json` (clone com push).
2. Pauta F = "Aprovado" e fila "aguardando" → fila `"status": "aprovado"`; Pauta G = "Na fila". F = "Recusado" → fila "recusado", G = "Recusado".
3. Para cada post que virou aprovado: acrescente os produtos na aba **Produtos** (A nome · B loja · C preço número · D link de afiliado · E post id · F "Na fila" · G data de hoje · I link_canal se Shopee). Não repita produto que já está lá.
4. Fila "publicado" → Pauta G = "Publicado", H = `{"markdown":"[abrir](<link>)"}`; aba **Posts**: nova linha (Nº seguinte com apóstrofo, tema, loja, formato, data, F "Ativa", G pasta_mac) se ainda não existir.
5. Fila "erro" → Pauta G = "Erro" e I = a mensagem; avise a Carol.
6. Aba **Aprovar** (achadinhos avulsos pro canal): linha com F = "Aprovado", Observação (H) com "link de afiliado pronto" e que ainda não está na aba Produtos (compare pelo link) → nova linha em **Produtos**: A = Sugestão, B = Loja, C = Preço (número), D = o link de dentro da coluna E (só a URL), E = "canal", F = "Na fila", G = data de hoje, I = a URL depois de "canal: " na Observação (só Shopee tem). F = "Recusado" → não faz nada.
7. Commit/push da fila se mudou. Mensagem final só se algo mudou (1–3 linhas); se nada mudou: "sem novidades".
