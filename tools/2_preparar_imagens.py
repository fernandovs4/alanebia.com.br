"""Passo 2 - Recorta e otimiza as fotos usando o ponto focal que o Gemini achou.

Entrada : tools/dados/fotos.json (do passo 1)
Saida   : site/assets/img/galeria/*  +  site/assets/data/galeria.json

Para cada foto gera:
  - recorte 4:5 (retrato) centrado nos rostos, em 700px e 1400px
  - versao grande para o lightbox (lado maior de 1800px)
  - tudo em WebP (leve) com JPG de reserva
"""
import hashlib, json, os, re, sys, unicodedata
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(__file__))
import gemini

BASE = gemini.BASE
SITE = os.path.join(BASE, "site")
FICHAS = os.path.join(BASE, "tools", "dados", "fotos.json")
DESTINO = os.path.join(BASE, "site", "assets", "img", "galeria")
MANIFESTO = os.path.join(BASE, "site", "assets", "data", "galeria.json")

# capitulo -> (ordem na historia, rotulo curto)
CAPITULOS = {
    "petrolina":   (1, "Petrolina"),
    "distancia":   (2, "A distancia"),
    "fortaleza":   (3, "Fortaleza"),
    "limeira":     (4, "Limeira"),
    "insper":      (5, "Insper"),
    "apartamento": (6, "Campo Belo"),
    "collie":      (7, "Collie"),
    "veleiro":     (8, "O veleiro"),
    "civil":       (9, "O civil"),
    "hoje":        (10, "Hoje"),
    "geral":       (11, "Momentos"),
}

def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return re.sub(r"-+", "-", t)

def recorta_focal(im, alvo_w, alvo_h, fx, fy):
    """Recorta na proporcao alvo mantendo o ponto focal (fx, fy) visivel e centrado."""
    w, h = im.size
    prop_alvo = alvo_w / alvo_h
    prop_orig = w / h

    if prop_orig > prop_alvo:          # original mais largo -> corta as laterais
        nova_w = int(round(h * prop_alvo)); nova_h = h
    else:                              # original mais alto -> corta topo/base
        nova_w = w; nova_h = int(round(w / prop_alvo))

    # centraliza no ponto focal, sem estourar as bordas
    esq = int(round(fx * w - nova_w / 2))
    topo = int(round(fy * h - nova_h / 2))
    esq = max(0, min(esq, w - nova_w))
    topo = max(0, min(topo, h - nova_h))

    return im.crop((esq, topo, esq + nova_w, topo + nova_h)).resize(
        (alvo_w, alvo_h), Image.LANCZOS)

def protege(im, caixas, margem=0.015):
    """Borra os trechos com dado pessoal que o Gemini encontrou.

    O site e publico, entao CPF, matricula de certidao, nome impresso em
    documento e QR code nao podem ficar legiveis. As caixas vem em coordenadas
    normalizadas de 0 a 1000, no formato [ymin, xmin, ymax, xmax].

    A borda do borrao e suavizada de proposito: um retangulo cinza duro parece
    censura, enquanto o desfoque esfumacado passa por profundidade de campo.
    """
    if not caixas:
        return im
    w, h = im.size
    raio = max(14, int(min(w, h) * 0.055))

    # mascara branca onde deve borrar, depois esfumacada nas bordas
    mascara = Image.new("L", (w, h), 0)
    pincel = ImageDraw.Draw(mascara)
    for y1, x1, y2, x2 in caixas:
        e = max(0, int((x1 / 1000 - margem) * w))
        t = max(0, int((y1 / 1000 - margem) * h))
        d = min(w, int((x2 / 1000 + margem) * w))
        b = min(h, int((y2 / 1000 + margem) * h))
        if d - e > 2 and b - t > 2:
            pincel.rectangle([e, t, d, b], fill=255)

    if not mascara.getbbox():
        return im

    esfuma = max(10, int(min(w, h) * 0.035))
    mascara = mascara.filter(ImageFilter.GaussianBlur(esfuma))
    # depois de esfumacar, reforca o miolo para o centro ficar 100% borrado
    mascara = mascara.point(lambda v: min(255, int(v * 1.8)))

    borrada = im.filter(ImageFilter.GaussianBlur(raio))
    return Image.composite(borrada, im, mascara)


def realca(im, nota):
    """Um leve tratamento nas fotos mais fraquinhas: contraste e cor."""
    if nota >= 8:
        return im
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.05)
    im = ImageEnhance.Sharpness(im).enhance(1.15)
    return im

def salva(im, caminho_sem_ext, qual_webp=82, qual_jpg=86):
    im.save(caminho_sem_ext + ".webp", "WEBP", quality=qual_webp, method=6)
    im.save(caminho_sem_ext + ".jpg", "JPEG", quality=qual_jpg, optimize=True, progressive=True)

def main():
    fichas = json.load(open(FICHAS, encoding="utf-8"))
    os.makedirs(DESTINO, exist_ok=True)
    os.makedirs(os.path.dirname(MANIFESTO), exist_ok=True)

    itens = []
    for ficha in fichas.values():
        origem = os.path.join(BASE, ficha["arquivo"])
        if not os.path.exists(origem):
            print(f"  x sumiu: {ficha['arquivo']}")
            continue
        if ficha.get("pessoas") == "nenhuma" and ficha.get("qualidade", 0) < 7:
            print(f"  - pulando (fraca e sem gente): {os.path.basename(origem)}")
            continue

        cap = ficha.get("capitulo", "geral")
        if cap not in CAPITULOS:
            cap = "geral"
        # O id vem do NOME DO ARQUIVO, nunca da legenda. Se viesse da legenda,
        # reanalisar as fotos mudaria os ids e quebraria os caminhos escritos
        # a mao no index.html. Assim o id de uma foto e o mesmo para sempre.
        digital = hashlib.md5(ficha["arquivo"].encode("utf-8")).hexdigest()[:8]
        nome = f"{cap}-{digital}"

        im = ImageOps.exif_transpose(Image.open(origem)).convert("RGB")
        caixas = ficha.get("dados_sensiveis") or []
        if caixas:
            print(f"     (borrando {len(caixas)} trecho(s) com dado pessoal)")
        im = protege(im, caixas)
        im = realca(im, ficha.get("qualidade", 5))
        fx, fy = ficha.get("foco_x", 0.5), ficha.get("foco_y", 0.4)

        # cartao da galeria, 4:5
        salva(recorta_focal(im, 700, 875, fx, fy), os.path.join(DESTINO, nome + "-700"))
        salva(recorta_focal(im, 1400, 1750, fx, fy), os.path.join(DESTINO, nome + "-1400"))

        # versao cheia para o lightbox
        cheia = im.copy(); cheia.thumbnail((1800, 1800), Image.LANCZOS)
        salva(cheia, os.path.join(DESTINO, nome + "-cheia"), 80, 84)

        ordem, rotulo = CAPITULOS[cap]
        itens.append({
            "id": nome,
            "capitulo": cap,
            "rotulo": rotulo,
            "ordem": ordem,
            "legenda": ficha.get("legenda", ""),
            "alt": ficha.get("alt", ficha.get("descricao", "")),
            "descricao": ficha.get("descricao", ""),
            "clima": ficha.get("clima", ""),
            "nota": ficha.get("qualidade", 5),
            "destaque": bool(ficha.get("bom_para_destaque")),
            "cheia": {"w": cheia.width, "h": cheia.height},
            "protegida": bool(caixas),
        })
        print(f"  ok {nome}")

    itens.sort(key=lambda x: (x["ordem"], -x["nota"]))
    pacote = {"fotos": itens}

    json.dump(pacote, open(MANIFESTO, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # a mesma coisa como .js: assim a galeria funciona ate abrindo o
    # index.html direto do disco (file://), onde o fetch e bloqueado
    js = os.path.splitext(MANIFESTO)[0] + ".js"
    with open(js, "w", encoding="utf-8") as f:
        f.write("/* Gerado por tools/2_preparar_imagens.py - nao edite a mao. */\n")
        f.write("window.GALERIA = ")
        json.dump(pacote, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"\n{len(itens)} fotos preparadas em {DESTINO}")
    print(f"Manifesto: {MANIFESTO}")
    print(f"Versao JS:  {js}")

    # carimba a versao no caminho do galeria.js dentro do index.html. Sem isso,
    # o navegador dos convidados continuaria mostrando a galeria antiga depois
    # de voces republicarem o site com fotos novas.
    html = os.path.join(BASE, "site", "index.html")
    if os.path.exists(html):
        texto = open(html, encoding="utf-8").read()
        atualizado = texto
        # cada arquivo ganha a versao do PROPRIO conteudo, entao o navegador so
        # rebaixa o que realmente mudou
        for caminho, dentro in ((js, "assets/data/galeria.js"),
                                (os.path.join(SITE, "css", "styles.css"), "css/styles.css"),
                                (os.path.join(SITE, "js", "main.js"), "js/main.js")):
            if not os.path.exists(caminho):
                continue
            versao = hashlib.md5(open(caminho, "rb").read()).hexdigest()[:8]
            alvo = re.compile(re.escape(dentro) + r"(\?v=[0-9a-f]+)?")
            atualizado = alvo.sub(lambda m, d=dentro, v=versao: f"{d}?v={v}", atualizado)
        if atualizado != texto:
            open(html, "w", encoding="utf-8").write(atualizado)
            print("index.html carimbado com as versoes dos arquivos")

if __name__ == "__main__":
    main()
