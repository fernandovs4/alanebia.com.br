"""Passo 1 - Le todas as fotos com o Gemini e salva a ficha tecnica de cada uma.

Entrada : fotos/*.jpg|jpeg|png  (e as fotos ja publicadas em site/assets/img/originais)
Saida   : tools/dados/fotos.json

Rode de novo sempre que adicionar fotos novas na pasta `fotos/`. Fotos ja
analisadas sao puladas, entao o custo e so das novas.
"""
import glob, hashlib, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gemini

BASE = gemini.BASE
SAIDA = os.path.join(BASE, "tools", "dados", "fotos.json")

PROMPT = """Voce e um diretor de arte analisando fotos para o site de casamento de Alan e Bia.

A historia deles: se conheceram numa acaiteria em Petrolina (PE) em dezembro de 2020;
namoraram a distancia (ele estudando em Fortaleza, ela na Unicamp em Limeira); ele se
formou no Insper em Sao Paulo; moram juntos no Campo Belo (SP) com a border collie
chamada Collie; casaram no civil em agosto de 2026; a festa e em 21/11/2026, em Petrolina.

Analise a imagem e responda SOMENTE com um JSON valido (sem markdown), com estas chaves:
{
  "descricao": "descricao objetiva da cena em pt-BR, 1 a 3 frases",
  "pessoas": "casal | ele | ela | casal+cachorro | cachorro | grupo | nenhuma",
  "cenario": "onde parece ser",
  "clima": "romantico | divertido | elegante | intimo | festivo | sereno | cotidiano",
  "qualidade": "nota de 1 a 10 para nitidez, luz e composicao - seja rigoroso",
  "orientacao": "retrato | paisagem | quadrada",
  "foco_x": "0.0 a 1.0 - posicao horizontal dos rostos",
  "foco_y": "0.0 a 1.0 - posicao vertical dos rostos",
  "bom_para_hero": true ou false,
  "bom_para_destaque": true ou false,
  "legenda": "legenda curta e calorosa em pt-BR, no maximo 7 palavras, sem ponto final",
  "alt": "texto alternativo descritivo em pt-BR para leitores de tela",
  "capitulo": "petrolina | distancia | fortaleza | limeira | insper | collie | apartamento | veleiro | civil | hoje | geral",
  "observacoes": "defeitos: desfoque, ruido, marca dagua, print de tela, etc",
  "tem_documento": true ou false
     // MUITO IMPORTANTE, o site e publico. Responda true se aparecer na foto
     // QUALQUER documento, papel impresso, tela, cartao, placa de carro,
     // codigo de barras ou QR code - mesmo que pequeno, torto ou desfocado.
     // Rosto de pessoa NAO conta.
}"""

PROMPT_CAIXA = """Nesta foto aparece um documento, papel impresso, tela, cartao,
placa de carro ou codigo (barras/QR) com informacao que pode ser pessoal.

Sua tarefa: devolver a caixa delimitadora que cobre TODA a area com texto impresso
ou preenchido, e tambem qualquer codigo de barras ou QR code. Seja GENEROSO - e
melhor cobrir area demais do que de menos. Se houver mais de um documento, devolva
uma caixa para cada. Se nao houver nada do tipo, devolva a lista vazia.

Responda SOMENTE com JSON:
{"caixas": [{"box_2d": [ymin, xmin, ymax, xmax], "rotulo": "o que e"}]}

Coordenadas normalizadas de 0 a 1000, onde [0,0] e o canto superior esquerdo e
[1000,1000] o canto inferior direito da imagem."""


def acha_dados_sensiveis(caminho):
    """Segundo passo: localiza com precisao a area do documento.

    A triagem do passo anterior usa o modelo rapido e so diz SE existe documento.
    Quando existe, chamamos o modelo maior com um prompt dedicado - ele acerta a
    caixa com muito mais precisao do que quando a pergunta vem junto de outras dez.
    """
    try:
        r = gemini.pergunta(PROMPT_CAIXA, imagens=[caminho],
                            modelo=gemini.TEXTO, temperatura=0.0)
    except RuntimeError as e:
        print(f"      ! nao consegui localizar o documento: {e}")
        return []

    bruto = r if isinstance(r, list) else r.get("caixas", [])
    caixas = []
    for c in bruto:
        try:
            y1, x1, y2, x2 = (float(v) for v in (c["box_2d"] if isinstance(c, dict) else c))
        except (TypeError, ValueError, KeyError):
            continue
        if x2 > x1 and y2 > y1:
            caixas.append([y1, x1, y2, x2])
    return caixas


def arquivos():
    """Lista as fotos, jogando fora as repetidas.

    E comum a mesma foto aparecer duas vezes na pasta - o WhatsApp salva com
    "(1)" no fim, ou a gente copia sem lembrar. Comparamos o conteudo byte a
    byte: se duas fotos sao identicas, so a primeira entra no site.
    """
    pastas = [os.path.join(BASE, "fotos"),
              os.path.join(BASE, "site", "assets", "img", "originais")]
    achados = []
    for pasta in pastas:
        for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
            achados += glob.glob(os.path.join(pasta, f"*.{ext}"))

    unicos, vistos, repetidas = [], {}, []
    for caminho in sorted(set(achados)):
        with open(caminho, "rb") as f:
            digital = hashlib.md5(f.read()).hexdigest()
        if digital in vistos:
            repetidas.append((caminho, vistos[digital]))
            continue
        vistos[digital] = caminho
        unicos.append(caminho)

    if repetidas:
        print(f"  {len(repetidas)} foto(s) repetida(s), fora do site:")
        for copia, original in repetidas:
            print(f"    - {os.path.basename(copia)}")
            print(f"      (igualzinha a {os.path.basename(original)})")
    return unicos

def main():
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    dados = {}
    if os.path.exists(SAIDA):
        dados = json.load(open(SAIDA, encoding="utf-8"))

    todos = arquivos()

    # limpa da ficha o que nao esta mais na lista (foto apagada ou repetida)
    validos = {os.path.relpath(c, BASE).replace(chr(92), "/") for c in todos}
    sumidas = [k for k in dados if k not in validos]
    for k in sumidas:
        del dados[k]
    if sumidas:
        print(f"  {len(sumidas)} foto(s) saiu(ram) da ficha (apagada ou repetida)")

    novos = 0
    for i, caminho in enumerate(todos, 1):
        nome = os.path.relpath(caminho, BASE).replace("\\", "/")
        if nome in dados and "--forcar" not in sys.argv:
            continue
        try:
            w, h = Image.open(caminho).size
        except Exception as e:
            print(f"  x nao consegui abrir {nome}: {e}")
            continue
        print(f"[{i}/{len(todos)}] lendo {os.path.basename(nome)} ...")
        ficha = gemini.pergunta(PROMPT, imagens=[caminho])
        ficha.update({"arquivo": nome, "largura": w, "altura": h})
        try:
            ficha["qualidade"] = int(float(ficha.get("qualidade", 5)))
            ficha["foco_x"] = min(1.0, max(0.0, float(ficha.get("foco_x", 0.5))))
            ficha["foco_y"] = min(1.0, max(0.0, float(ficha.get("foco_y", 0.4))))
        except (TypeError, ValueError):
            ficha["qualidade"], ficha["foco_x"], ficha["foco_y"] = 5, 0.5, 0.4

        caixas = []
        if ficha.get("tem_documento"):
            print("      . documento a vista, localizando com o modelo maior...")
            caixas = acha_dados_sensiveis(caminho)
        ficha["dados_sensiveis"] = caixas
        if caixas:
            print(f"      ! {len(caixas)} area(s) com dado pessoal -> serao borradas")
        elif ficha.get("tem_documento"):
            print("      ! documento detectado mas sem caixa. CONFIRA ESSA FOTO A MAO.")
        dados[nome] = ficha
        novos += 1
        print(f"      nota {ficha['qualidade']} | {ficha['pessoas']} | {ficha['capitulo']} | \"{ficha['legenda']}\"")
        json.dump(dados, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # grava sempre no fim: sem isso, uma rodada que so REMOVE fotos repetidas
    # (nenhuma foto nova) nunca chegaria a salvar a limpeza em disco
    json.dump(dados, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"\n{novos} foto(s) nova(s). Total no arquivo: {len(dados)}")
    print(f"Salvo em {SAIDA}")

if __name__ == "__main__":
    main()
