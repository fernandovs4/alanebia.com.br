# alanebia.com.br

Site estático publicado via GitHub Pages a partir da branch `main` (raiz).

- Domínio: https://alanebia.com.br (arquivo `CNAME`)
- Para publicar: mergear na `main`.

## Deploy

Push/merge na `main` dispara `.github/workflows/deploy.yml`, que publica a raiz do repo no GitHub Pages (modo GitHub Actions). Também dá pra rodar manualmente em Actions → "Deploy para GitHub Pages" → Run workflow.
