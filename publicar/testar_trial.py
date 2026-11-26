"""Teste seguro: cria um container de Reels em modo TESTE (trial) com o vídeo de hoje e confere se ficou pronto.
NÃO publica nada. Containers não publicados expiram sozinhos em 24 h."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import publicar as p

base = "https://carolixas.github.io/robo-achadinhos/m/posts/2026-11-26-reels-a/"
cid = p.chamar("POST", f"{p.IG_ID}/media", media_type="REELS", video_url=base + "reels.mp4",
               cover_url=base + "capa.jpg", caption="teste", trial_params=p.TRIAL)["id"]
p.esperar_pronto(cid)
print("OK: container de Reels em modo teste pronto (não publicado):", cid)
