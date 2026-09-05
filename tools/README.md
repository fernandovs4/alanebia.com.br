# Ferramentas — como o site se monta sozinho

Estes quatro scripts fazem o trabalho chato: **ler as fotos, escolher o
recorte, escrever as legendas, proteger dados pessoais e gerar as artes**.
Quem faz a leitura é o Gemini; quem corta e otimiza é o Python.

Na prática, adicionar fotos novas ao site é isto:

```bash
# 1. a chave da API, uma vez por sessão do terminal
export GEMINI_API_KEY="sua-chave"

# 2. jogue as fotos novas em fotos/ e rode:
python tools/1_analisar_fotos.py
python tools/2_preparar_imagens.py
```

Pronto — a galeria, os filtros, as legendas e o lightbox já estão atualizados.

---

## Antes de começar

**Chave da API do Gemini** (grátis): pegue em
[aistudio.google.com/apikey](https://aistudio.google.com/apikey).

Como definir a chave no terminal:

| Sistema | Comando |
|---|---|
| Windows (PowerShell) | `$env:GEMINI_API_KEY = "sua-chave"` |
| Windows (Git Bash) | `export GEMINI_API_KEY="sua-chave"` |
| Linux / macOS | `export GEMINI_API_KEY="sua-chave"` |

**Bibliotecas do Python** (só na primeira vez):

```bash
pip install pillow requests
```

---

## Os quatro passos

### `1_analisar_fotos.py` — o Gemini lê as fotos

Passa cada foto de `fotos/` pelo Gemini e guarda uma ficha técnica em
`tools/dados/fotos.json`.

Antes de qualquer coisa ele **descarta as fotos repetidas**, comparando o
conteúdo byte a byte — é comum a mesma foto aparecer duas vezes, com "(1)" no
fim do nome. Fotos que saíram da pasta também somem da ficha.

Para cada foto que sobra, ele descobre:

- o que está acontecendo na cena e quem aparece;
- **onde estão os rostos** (usado para o recorte não cortar cabeça);
- uma nota de qualidade de 1 a 10;
- a que capítulo da história a foto pertence;
- uma legenda curta e o texto alternativo para leitores de tela;
- se há **algum documento à vista** — e, quando há, uma segunda chamada (com o
  modelo maior e um prompt dedicado só a isso) localiza a área exata com CPF,
  matrícula, nomes ou QR code.

> As duas etapas existem por um motivo prático: quando a pergunta sobre o
> documento vinha junto das outras dez, o modelo até acusava a presença, mas
> errava feio a posição da caixa — borrava as flores em vez da certidão.
> Perguntando sozinho, com o modelo maior, ele acerta.

Fotos já analisadas são puladas, então rodar de novo só custa as fotos novas.
Para refazer tudo do zero: `python tools/1_analisar_fotos.py --forcar`.

### `2_preparar_imagens.py` — recorta, protege e otimiza

Lê a ficha do passo 1 e, para cada foto:

1. **borra os trechos com dado pessoal** que o passo 1 encontrou;
2. dá uma leve realçada nas fotos com nota mais baixa;
3. recorta em 4:5 **centrado nos rostos**, usando o ponto focal do Gemini;
4. gera as versões `-700`, `-1400` e `-cheia`, em WebP e JPG.

O borrão tem a borda esfumaçada de propósito: um retângulo cinza duro parece
censura, o desfoque suave passa por profundidade de campo.

O nome de cada arquivo vem do **nome da foto original**, não da legenda — assim
o caminho de uma foto nunca muda, mesmo que você mande reescrever as legendas.

No fim escreve `site/assets/data/galeria.json` e `galeria.js` — é de lá que a
galeria do site tira tudo — e carimba a versão no `index.html`, para o navegador
dos convidados não mostrar a galeria antiga depois de você republicar.

> A versão `.js` existe para a galeria funcionar mesmo abrindo o `index.html`
> com dois cliques. Navegador bloqueia `fetch` em `file://`.

### `3_gerar_arte.py` — as ilustrações

> Os arquivos originais (PNG de até 7 MB) ficam em `tools/masters/`, fora da
> pasta `site/`. Assim a pasta que você publica não carrega arquivos que o site
> nem usa. Quem gera as versões leves dentro de `site/` é o passo 4.

Usa o Gemini para gerar três peças (só uma vez; depois ele pula se o arquivo
já existe — use `--forcar` para refazer):

- **`hero-panoramico`** — a foto do civil, que é vertical, ampliada para
  panorâmica 16:9. O casal fica intacto; só o fundo ao redor é estendido, o que
  abre o espaço vazio à esquerda onde entram os nomes.
- **`mapa-rota`** — o mapa ilustrado do Brasil com a rota Petrolina → Fortaleza
  → Limeira → São Paulo → Petrolina, em traço dourado.
- **`ornamento-botanico`** — o galho de açaí com oliveira que separa as seções.

### `4_otimizar_arte.py` — deixa as artes leves

Gera as versões web das artes do passo 3 (várias larguras, WebP + JPG) e mais
duas coisas:

- um **recorte vertical do hero** para celular, feito da **foto original**, sem
  nenhuma interferência de IA;
- uma versão do ornamento **com fundo transparente**, para ele funcionar tanto
  sobre o creme quanto sobre o azul-escuro.

---

## Quando rodar cada um

| Situação | O que rodar |
|---|---|
| Adicionei fotos novas | passos 1 e 2 |
| Quero refazer as legendas | passo 1 com `--forcar`, depois o 2 |
| Quero um mapa ou ornamento diferente | passo 3 com `--forcar`, depois o 4 |
| Troquei a foto do hero | mude `HERO_ORIGEM` no passo 3, rode 3 `--forcar` e 4 |

---

## Conferir antes de publicar

O borrão de dados pessoais é automático, mas **vale conferir com o olho**:
abra a galeria do site e veja as fotos que envolvem documentos. Se alguma coisa
tiver escapado, dá para acrescentar a caixa na mão em `tools/dados/fotos.json`,
no campo `dados_sensiveis` da foto, e rodar o passo 2 de novo. O formato é
`[ymin, xmin, ymax, xmax]`, com valores de 0 a 1000:

```json
"dados_sensiveis": [[620, 40, 780, 560]]
```

---

## Modelos usados

Estão no topo de `gemini.py`, fáceis de trocar:

| Para quê | Modelo |
|---|---|
| Ler as fotos | `gemini-2.5-flash` |
| Textos mais elaborados | `gemini-3.1-pro-preview` |
| Gerar e editar imagens | `gemini-3-pro-image` |

---

## Se der problema

**"Defina a chave antes de rodar"** — a variável `GEMINI_API_KEY` não está
definida naquele terminal. Veja a tabela lá em cima. Fechou o terminal,
precisa definir de novo.

**"Gemini nao respondeu depois de varias tentativas"** — normalmente é limite
de uso da API. Espere um minuto e rode de novo; o passo 1 continua de onde
parou.

**A galeria sumiu do site** — provavelmente o `site/assets/data/galeria.js` não
existe. Rode o passo 2.

**Uma foto ficou com recorte estranho** — o Gemini errou o ponto focal. Abra
`tools/dados/fotos.json`, ache a foto e ajuste `foco_x` e `foco_y` (de 0 a 1,
onde `0.5` é o centro). Rode o passo 2 de novo.

**Quero tirar uma foto do site** — apague a entrada dela em
`tools/dados/fotos.json` e rode o passo 2. Ou tire a foto de `fotos/` e rode o
passo 1 com `--forcar`.
