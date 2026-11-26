# robo-achadinhos

Robô de ofertas do @achadosdascarois (privado).

## O que ele faz

Todo dia às **7h17** (horário de Brasília) o GitHub roda o `robo_nuvem.py`, que:

1. busca produtos de casa e decor no **AliExpress** pela API oficial de afiliados
   (6 buscas por dia, em rodízio, da lista em `config.json`);
2. fica só com o que tem preço entre R$ 12 e R$ 150, nota 4,6 ou mais e 200+ vendas;
3. tira o que já foi sugerido antes (`dados/ja_sugeridos.json`);
4. grava as 8 melhores em `sugestoes/ultimas.json` (e uma cópia com a data),
   já com **preço em reais** e **link de afiliado**.

Às 8h47 a tarefa agendada do Claude lê esse arquivo, escolhe as que combinam com o
perfil e coloca na aba **Aprovar** da planilha "Central Achadinhos das Carois".

## Chaves

As chaves ficam em **Settings → Secrets and variables → Actions** (nunca no código):

- `ALIEXPRESS_APP_KEY`
- `ALIEXPRESS_APP_SECRET`
- `ALIEXPRESS_TRACKING_ID` (ex.: `default`)

## Rodar na hora

Aba **Actions → Robô de ofertas → Run workflow**.

## Ajustar

Mude buscas, faixa de preço, nota e vendas mínimas em `config.json`.
