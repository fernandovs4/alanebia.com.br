"""Utilitarios compartilhados para falar com a API do Gemini.

A chave e lida da variavel de ambiente GEMINI_API_KEY.
"""
import base64, io, json, os, time
import requests
from PIL import Image

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(BASE, "site")

TEXTO   = "gemini-3.1-pro-preview"
RAPIDO  = "gemini-2.5-flash"
IMAGEM  = "gemini-3-pro-image"

def chave():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        raise SystemExit(
            "Defina a chave antes de rodar:\n"
            '  Windows PowerShell:  $env:GEMINI_API_KEY = "sua-chave"\n'
            '  Linux/macOS:         export GEMINI_API_KEY="sua-chave"'
        )
    return k

def _url(modelo):
    return f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={chave()}"

def b64_imagem(caminho, maxdim=1200, qualidade=85):
    im = Image.open(caminho).convert("RGB")
    im.thumbnail((maxdim, maxdim))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=qualidade)
    return base64.b64encode(buf.getvalue()).decode()

def pergunta(prompt, imagens=(), modelo=RAPIDO, json_saida=True, temperatura=0.4, tentativas=4):
    """Manda texto (+ imagens) e devolve a resposta. Com json_saida=True devolve dict."""
    partes = [{"text": prompt}]
    for cam in imagens:
        partes.append({"inline_data": {"mime_type": "image/jpeg", "data": b64_imagem(cam)}})
    corpo = {"contents": [{"parts": partes}],
             "generationConfig": {"temperature": temperatura}}
    if json_saida:
        corpo["generationConfig"]["responseMimeType"] = "application/json"

    for n in range(tentativas):
        try:
            r = requests.post(_url(modelo), json=corpo, timeout=180)
            if r.status_code == 200:
                txt = r.json()["candidates"][0]["content"]["parts"][-1]["text"]
                return json.loads(txt) if json_saida else txt
            print(f"  ! HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"  ! {e}")
        time.sleep(2 + n * 3)
    raise RuntimeError("Gemini nao respondeu depois de varias tentativas")

def gera_imagem(prompt, destino, referencias=(), proporcao="16:9", tamanho="2K", modelo=IMAGEM):
    """Gera (ou edita, se passar referencias) uma imagem e salva em `destino`."""
    partes = [{"text": prompt}]
    for cam in referencias:
        with open(cam, "rb") as f:
            partes.append({"inline_data": {"mime_type": "image/jpeg",
                                           "data": base64.b64encode(f.read()).decode()}})
    corpo = {"contents": [{"parts": partes}],
             "generationConfig": {"imageConfig": {"aspectRatio": proporcao, "imageSize": tamanho}}}
    r = requests.post(_url(modelo), json=corpo, timeout=600)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
    for p in r.json()["candidates"][0]["content"]["parts"]:
        d = p.get("inlineData") or p.get("inline_data")
        if d:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, "wb") as f:
                f.write(base64.b64decode(d["data"]))
            return destino
    raise RuntimeError("A resposta nao trouxe nenhuma imagem")
