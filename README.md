# alanebia.com.br

**Alan & Bia · 21 de novembro de 2026 · Petrolina, PE**

Site do casamento e as ferramentas que o montam. Eles se conheceram numa
açaiteria em Petrolina, em dezembro de 2020 — a festa volta pro lugar onde
tudo começou.

Site no ar: **https://alanebia.com.br**

## O que tem aqui

| Pasta | O que é |
|---|---|
| [`site/`](site/) | O site em si — HTML, CSS e JavaScript puros, sem build. É esta pasta que vai pro ar. Abra `site/index.html` no navegador e pronto. |
| [`tools/`](tools/) | Scripts Python que leem as fotos com o Gemini, escolhem o recorte, escrevem as legendas e geram as artes. |
| `fotos/` | As fotos originais, entrada do pipeline. |

Cada pasta tem seu próprio README com as instruções.

## Rodar localmente

```bash
cd site
python -m http.server 8000
# abra http://localhost:8000
```

## Deploy

Push ou merge na `main` dispara `.github/workflows/deploy.yml`, que publica no
GitHub Pages. Também dá pra rodar à mão em Actions → "Deploy para GitHub Pages"
→ Run workflow.

**O workflow publica a pasta `site/`, não a raiz.** É de propósito: mantém
`fotos/` e `tools/` no repositório sem servi-los no domínio. Se um dia o site
virar um projeto Node (React/Vite/CRA), basta ter um `package.json` na raiz —
o workflow detecta, roda `npm ci && npm run build` e publica `dist/` (ou
`build/`), copiando `index.html` para `404.html` para as rotas de SPA
sobreviverem a um refresh.

O domínio próprio está no arquivo `CNAME`, que o workflow copia para dentro do
que é publicado.

## Atualizar a galeria com fotos novas

```bash
export GEMINI_API_KEY="sua-chave"   # PowerShell: $env:GEMINI_API_KEY = "sua-chave"
# jogue as fotos em fotos/ e rode:
python tools/1_analisar_fotos.py
python tools/2_preparar_imagens.py
```

Detalhes em [`tools/README.md`](tools/README.md).
