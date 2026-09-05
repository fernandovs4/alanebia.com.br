"""Passo 3 - Cria com o Gemini as artes que o site usa.

  - hero panoramico: estende a foto do civil para 16:9, com espaco para o texto
  - mapa ilustrado do Brasil com a rota da historia
  - ornamento botanico (galho de acai + oliveira) usado como divisor

Saida: tools/masters/
Ja existe? Pula. Use --forcar para refazer tudo.
"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gemini

BASE = gemini.BASE
# Os masters (PNG gigantes) ficam FORA de site/, senao a pasta publicada
# levaria 8 MB de arquivos que o site nem usa. Quem gera as versoes leves
# dentro de site/ e o passo 4.
ARTE = os.path.join(BASE, "tools", "masters")
FOTOS = os.path.join(BASE, "fotos")

HERO_ORIGEM = "WhatsApp Image 2026-08-08 at 13.45.42 (1).jpeg"

PECAS = [
    dict(
        nome="hero-panoramico",
        proporcao="16:9", tamanho="4K",
        referencia=HERO_ORIGEM,
        prompt=(
            "Outpaint / uncrop this photograph into a wide 16:9 cinematic landscape frame. "
            "CRITICAL: keep the two people EXACTLY as they are - do not alter their faces, skin, "
            "expressions, bodies, clothing, hands, hair or the gold ring in any way whatsoever. "
            "Keep them at the same scale, positioned on the right third. Extend ONLY the surrounding "
            "environment: continue the warm out-of-focus interior background (wooden slat wall, soft "
            "warm bokeh lights, cream and terracotta tones) naturally and photorealistically. Match the "
            "original film grain, lens blur, depth of field and colour grading precisely. Large empty "
            "softly-blurred negative space on the LEFT HALF for text overlay. No text, no watermark, "
            "no additional people."
        ),
    ),
    dict(
        nome="mapa-rota",
        proporcao="4:3", tamanho="2K",
        prompt=(
            "An elegant hand-drawn illustrated map of Brazil for luxury wedding stationery. Style: "
            "single-weight fine ink line art in warm gold (#C6A75E) on a plain solid cream background "
            "(#FAF3ED), delicate, airy, editorial. Show a simplified outline of Brazil. Mark five cities "
            "with small solid dots and a tiny hand-drawn icon beside each: Petrolina in Pernambuco (a "
            "small acai bowl), Fortaleza in Ceara (a lighthouse), Limeira in Sao Paulo state (an open "
            "book), Sao Paulo city (a small skyline), and back to Petrolina (a tiny heart). Connect them "
            "in that order with a delicate dashed travel line that loops back to Petrolina. Small compass "
            "rose in a corner. Label ONLY those five city names in a fine elegant serif, nothing else. "
            "Flat 2D, no shadows, no gradients, generous white space."
        ),
    ),
    dict(
        nome="ornamento-botanico",
        proporcao="16:9", tamanho="1K",
        prompt=(
            "A delicate botanical divider ornament for wedding stationery. Fine continuous single-weight "
            "line art in warm gold (#C6A75E) on a plain solid cream background (#FAF3ED). Subject: a "
            "horizontal symmetrical sprig - acai palm fronds with small berry clusters on the left, olive "
            "branch with leaves on the right, meeting at a tiny centred heart. Extremely minimal, "
            "hand-drawn ink feel, flat 2D, no shadows, no text, wide thin composition with generous "
            "empty margins above and below."
        ),
    ),
]

def main():
    os.makedirs(ARTE, exist_ok=True)
    forcar = "--forcar" in sys.argv

    for peca in PECAS:
        destino = os.path.join(ARTE, peca["nome"] + ".png")
        if os.path.exists(destino) and not forcar:
            print(f"  - ja existe, pulando: {peca['nome']}")
            continue
        refs = []
        if peca.get("referencia"):
            refs = [os.path.join(FOTOS, peca["referencia"])]
            if not os.path.exists(refs[0]):
                print(f"  x foto de referencia nao encontrada: {peca['referencia']}")
                continue
        print(f"  ... gerando {peca['nome']} ({peca['proporcao']}, {peca['tamanho']})")
        gemini.gera_imagem(peca["prompt"], destino, referencias=refs,
                           proporcao=peca["proporcao"], tamanho=peca["tamanho"])
        print(f"  ok {peca['nome']} -> {Image.open(destino).size}")

    print(f"\nArtes em {ARTE}")

if __name__ == "__main__":
    main()
