# Mudança do Mac para o PC Windows (27/11/2026)

A Carol quer liberar o MacBook. Tudo que dependia do Mac passa a rodar numa conversa aberta **no app do Claude no PC Windows**, com a pasta `Documentos\Achadinhos Carolixas` conectada. Tarefas criadas a partir dessa conversa ficam presas ao PC (não ao Mac).

O que já está fora de qualquer computador (não mexer): publicação no Instagram e respostas do "comenta QUERO" (GitHub Actions), tarefa "Sincronizar pauta ↔ Instagram" (nuvem).

## Passos para a conversa do PC
0. `add_repo` carolixas/robo-achadinhos com acesso **push**, clone e leia este arquivo e `producao/ROTEIRO.md`. Regras de sempre: a Carol faz os logins; nunca leia `chaves-e-ajustes.txt`; só a Carol aprova posts; lojas só leitura.
1. Confira com `get_device_info` que o computador é o PC (Windows) e qual é o caminho da pasta conectada. Confira que existe a subpasta `musicas` com 10 mp3 (a Carol baixou da conversa antiga). Se não existir, avise a Carol e siga.
2. Chrome: `list_connected_browsers` → `select_browser` no osPlatform "Windows". Confira o WhatsApp Web (já logado) e a Amazon (já logada; SiteStripe funciona). Se a Shopee afiliados ou o AliExpress pedirem login, só avise a Carol.
3. Crie as 2 tarefas do canal (create_trigger, initiation human_request, `requires_local_device: true`, sem folders, notifications {}):
   - "Canal WhatsApp PC: achadinho da hora cheia (:03)" — cron `CRON_TZ=America/Sao_Paulo 3 8-23 * * *`
   - "Canal WhatsApp PC: achadinho do meio da hora (:33)" — cron `CRON_TZ=America/Sao_Paulo 33 8-22 * * *`
   - prompt das duas: o texto completo de `producao/canal_prompt.md` (copie exatamente).
4. Produção diária: `send_later` nesta conversa do PC para amanhã às 08:13 `[America/Sao_Paulo]`, nome "Produção diária: 2 Reels + 1 carrossel", initiation `human_schedule`, mensagem:
   "Hora da produção diária do @achadosdascarois (2 Reels + 1 carrossel para HOJE). Siga producao/ROTEIRO.md do repo carolixas/robo-achadinhos (git pull antes), parte "Roteiro da produção diária", incluindo as "Lições". Use o Chrome do PC Windows para as lojas e links de afiliado, a pasta conectada do PC para as músicas, e o container para renderizar. Posts entram na fila como "aguardando" e na aba Pauta com F "Aguardando" — quem aprova é a Carol; nunca marque aprovado nem publique direto. Só ler as lojas (nada de comprar/carrinho/cupom/login/captcha). Nunca leia chaves-e-ajustes.txt. No fim, mande à Carol (SendUserMessage) "Pauta de hoje pronta 👇", uma linha por post (tipo · tema · horário) e "Aprova na aba Pauta (tem prévia de cada um) que eu publico sozinha no horário." Se o PC/Chrome não responder, avise em 1 linha."
   - Lembrete ManyChat: `send_later` para 2026-11-30T10:00:00[America/Sao_Paulo], nome "ManyChat: fim do teste grátis", initiation human_request, mensagem: "Lembrete que a Carol pediu: hoje (30/11) acaba o teste grátis do ManyChat na conta Achadinhos das Carois. Avise em 3–4 linhas, sugira conferir em Configurações → Assinaturas se há cartão e se vai ser cobrado, e pergunte se ela quer manter o Pro ou voltar ao grátis. Não faça nada antes de ela responder."
5. Desligue (update_trigger `enabled: false`, a Carol pediu) as tarefas antigas presas ao Mac — só DEPOIS que as novas existirem:
   - trig_01B9YwFQ4CLjhaDJ8jTXajH4 (canal :03 do Mac)
   - trig_01WygAWbC5NZBe8y7hspyb53 (canal :33 do Mac)
   - trig_01YQHJbxtWhRNbQjoj8NbHDt (produção de 28/11 marcada pelo Mac)
   - trig_016RdygxWhLYHtkqZkvUyc5g (lembrete ManyChat do Mac)
   Se o sistema não deixar desligar, peça para a Carol desligar no menu "Agendados" do app.
6. Teste: rode à mão o passo a passo do canal 1 vez (mesmo texto de `producao/canal_prompt.md`) no Chrome do PC, e mande à Carol 1 linha com o que saiu.
7. Responda à Carol, curto: o que ficou ligado no PC, o que ela ainda precisa fazer (Windows: Configurações › Sistema › Energia › Suspender = Nunca; deixar Chrome e o app do Claude abertos; login Shopee afiliados/AliExpress se faltou) e que o Mac já pode ser fechado.
