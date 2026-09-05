# alanebia.com.br

Site estático publicado via GitHub Pages a partir da branch `main` (raiz).

- Domínio: https://alanebia.com.br (arquivo `CNAME`)
- Para publicar: mergear na `main`.

## Deploy

Push/merge na `main` dispara `.github/workflows/deploy.yml` (modo GitHub Actions). Também dá pra rodar manualmente em Actions → "Deploy para GitHub Pages" → Run workflow.

O workflow detecta o tipo do site:

- **Sem `package.json`** (HTML estático): publica a raiz do repo.
- **Com `package.json`** (React/Vite/CRA): roda `npm ci && npm run build` e publica `dist/` (ou `build/`). Copia `index.html` para `404.html` para rotas de SPA funcionarem no refresh.

O domínio próprio está na raiz, então o `base` do Vite fica o padrão `/`.
