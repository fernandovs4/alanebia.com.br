# Site do casamento — Alan & Bia

**21 de novembro de 2026 · Petrolina, PE**

Site estático (HTML + CSS + JavaScript puros). Não precisa instalar nada para
ver: é só abrir o `index.html` no navegador.

---

## O que dá para editar sem mexer em código

Quase tudo o que muda com frequência está no topo do arquivo `js/main.js`, num
bloco chamado `CONFIG`:

| O que | Onde |
|---|---|
| **Link do formulário de confirmação** | `CONFIG.linkConfirmacao` |
| Data e hora do casamento | `CONFIG.dataCasamento` (o mês começa em 0, então `10` = novembro) |
| Chave Pix | `CONFIG.pix.chave` |
| Endereço para presentes | `CONFIG.endereco` |
| Texto do evento no arquivo de agenda | `CONFIG.evento` |

### O link do formulário — falta preencher

Hoje está com um endereço de exemplo:

```js
linkConfirmacao: 'https://forms.gle/COLOQUE-O-LINK-AQUI',
```

Enquanto esse texto estiver aí, o botão **não** leva a lugar nenhum: ele mostra
um aviso dentro do próprio pop-up dizendo que o link ainda não foi configurado.
Troque pelo endereço real (Google Forms, Typeform, o que vocês usarem) e o botão
passa a abrir o formulário numa aba nova.

### Como funciona a confirmação de presença

Não há formulário dentro do site. Em vez disso:

1. Cinco botões **"Confirmar presença"** espalhados pela página (capa, save the
   date, card de presentes, faixa de presença e rodapé) abrem o mesmo pop-up.
2. O pop-up explica o Pix (lua de mel e reformas da casa nova), mostra a chave
   com botão de copiar, e traz o endereço para quem preferir mandar algo.
3. O botão dourado **"Ir para a confirmação"** manda para o
   `CONFIG.linkConfirmacao`.

### Outros textos

- História, capítulos e legendas: `index.html`, seção `NOSSA HISTÓRIA`.
- Cerimônia, recepção, traje e presentes: `index.html`, seção `O GRANDE DIA`.
- Perguntas frequentes: `index.html`, seção `DÚVIDAS`.

---

## Adicionando fotos novas

O trabalho pesado é automático. Jogue as fotos na pasta `fotos/` (na raiz do
projeto, um nível acima desta) e rode os passos descritos em
[`../tools/README.md`](../tools/README.md).

Em resumo:

```bash
# a chave da API do Gemini, uma vez por sessão do terminal
export GEMINI_API_KEY="sua-chave"          # Windows: $env:GEMINI_API_KEY = "sua-chave"

python tools/1_analisar_fotos.py           # o Gemini lê cada foto nova
python tools/2_preparar_imagens.py         # recorta, otimiza e monta a galeria
```

O site se atualiza sozinho: os filtros por capítulo, as legendas, os textos
alternativos e o lightbox saem todos da leitura que o Gemini fez.

---

## Privacidade das fotos

O passo 1 procura **dados pessoais legíveis** em cada foto (CPF, matrícula de
certidão, nome impresso em documento, endereço, placa de carro). O passo 2
borra automaticamente esses trechos antes de publicar.

Isso já pegou duas fotos da certidão de casamento, onde apareciam legíveis o
CPF dos dois, os nomes completos, a filiação, o número de matrícula e um QR
code. Nas duas o documento agora está desfocado.

**Mesmo assim, confira com o olho antes de publicar.** A detecção é boa, mas
não é infalível — na primeira tentativa ela errou o alvo e borrou as flores.
Abra a galeria, olhe as fotos que envolvem documentos e confirme. Se algo
escapar, dá para marcar a área na mão: veja
[`../tools/README.md`](../tools/README.md).

---

## Como ver o site no computador

Abrir o `index.html` com dois cliques funciona. Se quiser conferir exatamente
como vai ficar publicado, rode um servidor local:

```bash
cd site
python -m http.server 8000
```

E acesse `http://localhost:8000`.

### Endereço especial para conferência

`index.html?estatico=1` abre o site com todas as animações desligadas. Útil
para revisar textos, conferir o layout inteiro de uma vez ou imprimir.

---

## Como publicar na internet

Qualquer hospedagem de site estático serve. As mais fáceis:

1. **Netlify Drop** (grátis) — acesse [app.netlify.com/drop](https://app.netlify.com/drop)
   e arraste a pasta `site` inteira para a página. Fica no ar na hora.
2. **Vercel** ou **GitHub Pages** — também funcionam sem mudar nada.
3. Depois dá para apontar um domínio próprio, tipo `alanebia.com.br`.

### Antes de publicar

Pode arrastar a pasta `site` inteira, sem medo: os arquivos pesados (os `.png`
originais das artes, de 7 MB) ficam guardados fora dela, em `tools/masters/`.
A pasta publicada tem cerca de 22 MB, quase tudo foto de galeria.

Quando você republicar, os endereços do CSS, do JavaScript e do arquivo da
galeria mudam sozinhos (`styles.css?v=...`). Isso é de propósito: sem esse
número, o navegador dos convidados continuaria mostrando a versão antiga.

---

## O que o site tem

**Estrutura**

- Capa com a foto do civil ampliada para panorâmica, poeira dourada animada e contagem regressiva.
- Botão que gera um arquivo `.ics` na hora, para salvar na agenda do celular.
- Mapa ilustrado do Brasil ao lado da lista de paradas, com os pontos acendendo em sequência.
- Linha do tempo com sete capítulos, trilho dourado que se desenha conforme a rolagem e contadores de distância (800 km → 150 km → 0 km).
- Faixa da Collie, a madrinha.
- Galeria com filtro por capítulo, mosaico e lightbox (setas do teclado e arrastar no celular funcionam).
- Pop-up de confirmação de presença com Pix, endereço e botão para o formulário — acessível pelo teclado, fecha no Esc e devolve o foco a quem o abriu.
- Perguntas frequentes em sanfona.

**Detalhes técnicos**

- Rolagem suave com [Lenis](https://github.com/darkroomengineering/lenis) e [GSAP](https://gsap.com), carregados por CDN. **Se as bibliotecas não carregarem, o site continua funcionando** — só fica sem o embalo da rolagem.
- Imagens em WebP com JPG de reserva, em vários tamanhos, escolhidas conforme a tela.
- Respeita `prefers-reduced-motion`: quem configurou o sistema para menos animação vê o site parado.
- Navegação por teclado, foco visível, textos alternativos em todas as fotos.
- Dados estruturados (`schema.org/Event`) para o Google mostrar a data direito.

---

## Paleta e fontes

| Cor | Código |
|---|---|
| Azul | `#1F3A44` |
| Oliva | `#4E5B3C` |
| Rosé | `#D8A7A0` |
| Ouro | `#C6A75E` |
| Creme | `#FAF3ED` |

Fontes: **Fraunces** (títulos), **Newsreader** (texto), **Jost** (rótulos), via
Google Fonts. Tudo definido como variáveis no topo de `css/styles.css` — mudar
lá muda o site inteiro.


---

## Sobre o tamanho da página

A página tem cerca de **12 telas de rolagem** no computador. Ela já foi bem
maior — 21 telas — e encolheu tirando o que se repetia:

- fotos duplicadas (o passo 1 agora descarta sozinho as fotos iguais);
- a seção que só tinha uma frase de efeito sobre o açaí, ideia que já aparecia
  na capa, no capítulo 01 e no rodapé;
- a seção de pedido de música, que só apontava para o mesmo pop-up da seção
  logo acima;
- a linha do tempo, que tinha o trilho no meio e deixava metade da largura
  vazia em cada capítulo;
- nove capítulos que viraram sete, com textos mais curtos.

Se for acrescentar seção nova, vale olhar esse histórico antes: quase todo
crescimento veio de dizer a mesma coisa duas vezes.
