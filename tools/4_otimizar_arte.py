"""Passo 4 - Transforma as artes grandes em arquivos leves para a web.

Entrada : tools/masters/*.png (do passo 3)
Saida   : site/assets/img/arte/*-{largura}.{webp,jpg}
"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gemini

MASTERS = os.path.join(gemini.BASE, "tools", "masters")
ARTE = os.path.join(gemini.BASE, "site", "assets", "img", "arte")
FOTOS = os.path.join(gemini.BASE, "fotos")

# nome do master -> larguras a gerar
PLANO = {
    "hero-panoramico":     [1280, 1920, 2560],
    "mapa-rota":           [900, 1500],
    "ornamento-botanico":  [700, 1100],
}

# recorte vertical do hero para celular, feito da FOTO ORIGINAL (sem IA)
HERO_MOBILE_ORIGEM = "WhatsApp Image 2026-08-08 at 13.45.42 (1).jpeg"

def salva(im, base, qw=80, qj=85):
    im.save(base + ".webp", "WEBP", quality=qw, method=6)
    im.save(base + ".jpg", "JPEG", quality=qj, optimize=True, progressive=True)
    kb = os.path.getsize(base + ".webp") // 1024
    print(f"     {os.path.basename(base)}  {im.width}x{im.height}  {kb} KB")

def para_transparente(im, ganho=1.45, corte=26):
    """Tira o fundo creme de uma arte em traco, deixando so as linhas.

    A arte vem do Gemini como linhas douradas sobre creme chapado. Para o
    ornamento funcionar tambem sobre o fundo azul-escuro do site, medimos o
    quanto cada pixel se afasta da cor de fundo e usamos isso como opacidade.
    """
    im = im.convert("RGB")
    canto = im.crop((0, 0, max(4, im.width // 40), max(4, im.height // 40)))
    fundo = tuple(int(c) for c in canto.resize((1, 1), Image.LANCZOS).getpixel((0, 0)))

    px = im.load()
    alfa = Image.new("L", im.size)
    ap = alfa.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            d = max((fundo[0] - r) / max(1, fundo[0]),
                    (fundo[1] - g) / max(1, fundo[1]),
                    (fundo[2] - b) / max(1, fundo[2]))
            a = int(d * 255 * ganho)
            # o fundo "chapado" ainda tem um ruidinho: tudo que for quase
            # invisivel vira transparente de vez, senao a imagem fica pesada
            ap[x, y] = 0 if a < corte else min(255, a)
    saida = im.copy()
    saida.putalpha(alfa)
    return saida


def recorta_conteudo(im, folga=12):
    """Corta as bordas vazias de uma imagem com transparencia."""
    caixa = im.split()[-1].getbbox()
    if not caixa:
        return im
    e, t, d, b = caixa
    return im.crop((max(0, e - folga), max(0, t - folga),
                    min(im.width, d + folga), min(im.height, b + folga)))


def main():
    for nome, larguras in PLANO.items():
        master = os.path.join(MASTERS, nome + ".png")
        if not os.path.exists(master):
            print(f"  x master faltando: {nome}.png (rode o passo 3)")
            continue
        im = Image.open(master).convert("RGB")
        print(f"  {nome} ({im.width}x{im.height})")
        for w in larguras:
            if w > im.width:
                continue
            h = round(im.height * w / im.width)
            salva(im.resize((w, h), Image.LANCZOS), os.path.join(ARTE, f"{nome}-{w}"))

    # hero vertical para celular: recorte 4:5 da foto original, sem IA
    origem = os.path.join(FOTOS, HERO_MOBILE_ORIGEM)
    if os.path.exists(origem):
        print("  hero-retrato (recorte da foto original, sem IA)")
        im = Image.open(origem).convert("RGB")
        w, h = im.size
        alvo_h = min(h, round(w * 5 / 4))
        topo = max(0, min(int(h * 0.34 - alvo_h / 2), h - alvo_h))
        rec = im.crop((0, topo, w, topo + alvo_h))
        for lw in (800, 1200):
            lh = round(rec.height * lw / rec.width)
            salva(rec.resize((lw, lh), Image.LANCZOS), os.path.join(ARTE, f"hero-retrato-{lw}"))

    # Artes em traco douradosobre creme viram PNG com fundo transparente. Sem
    # isso o retangulo creme da imagem aparece recortado contra o degrade da
    # secao, e a arte so funciona num fundo unico.
    transparentes = [
        ("ornamento-botanico", "ornamento-transparente", (700, 1100), True),
        ("mapa-rota", "mapa-transparente", (760, 1200), False),
    ]
    for master, saida, larguras, cortar in transparentes:
        origem = os.path.join(MASTERS, master + ".png")
        if not os.path.exists(origem):
            continue
        print(f"  {saida} (fundo removido)")
        t = para_transparente(Image.open(origem))
        if cortar:
            t = recorta_conteudo(t)
        for w in larguras:
            if w > t.width:
                continue
            h = round(t.height * w / t.width)
            r = t.resize((w, h), Image.LANCZOS)
            destino = os.path.join(ARTE, f"{saida}-{w}.webp")
            r.save(destino, "WEBP", quality=88, method=6, exact=True)
            r.save(destino[:-5] + ".png", "PNG", optimize=True)
            print(f"     {saida}-{w}  {w}x{h}  "
                  f"{os.path.getsize(destino) // 1024} KB")

    print(f"\nPronto. Arquivos em {ARTE}")

if __name__ == "__main__":
    main()
