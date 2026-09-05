# Alan & Bia

**21 de novembro de 2026 · Petrolina, PE**

Site do casamento e as ferramentas que o montam. Eles se conheceram numa
açaiteria em Petrolina, em dezembro de 2020 — a festa volta pro lugar onde
tudo começou.

## O que tem aqui

| Pasta | O que é |
|---|---|
| [`site/`](site/) | O site em si — HTML, CSS e JavaScript puros. Abra `site/index.html` no navegador e pronto, não precisa instalar nada. |
| [`tools/`](tools/) | Scripts Python que leem as fotos com o Gemini, escolhem o recorte, escrevem as legendas e geram as artes. |
| `fotos/` | As fotos originais, entrada do pipeline. |

Cada pasta tem seu próprio README com as instruções.

## Rodar o site

```bash
cd site
python -m http.server 8000
# abra http://localhost:8000
```

## Atualizar a galeria com fotos novas

```bash
export GEMINI_API_KEY="sua-chave"   # PowerShell: $env:GEMINI_API_KEY = "sua-chave"
# jogue as fotos em fotos/ e rode:
python tools/1_analisar_fotos.py
python tools/2_preparar_imagens.py
```

Detalhes em [`tools/README.md`](tools/README.md).
