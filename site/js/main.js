/* =========================================================================
   Alan & Bia — 21.11.2026 — Petrolina, PE

   >>> É AQUI QUE VOCÊS EDITAM AS INFORMAÇÕES <<<
   Tudo o que muda com frequência está no bloco CONFIG logo abaixo.
   ========================================================================= */

const CONFIG = {
  // Data e hora do casamento (ano, mês-1, dia, hora, minuto).
  // Atenção: o mês começa em 0 — 10 = novembro.
  dataCasamento: new Date(2026, 10, 21, 16, 0, 0),

  // >>> LINK DO FORMULÁRIO DE CONFIRMAÇÃO DE PRESENÇA <<<
  // Troque pelo endereço real (Google Forms, Typeform, o que vocês usarem).
  // É para cá que o botão do pop-up manda o convidado.
  linkConfirmacao: 'https://forms.gle/COLOQUE-O-LINK-AQUI',

  // Dados do pop-up de presença
  pix: {
    chave: '87991893823',
    // Como a chave aparece na tela. Use o mesmo texto que você diria a alguém.
    rotulo: 'Chave Pix'
  },

  endereco: {
    linha1: 'Rua José Batista Pereira, 51 — ap. 1910',
    linha2: 'Campo Belo · São Paulo · SP'
  },

  // Dados usados no arquivo de calendário (.ics)
  evento: {
    titulo: 'Casamento de Alan e Bia',
    local: 'Petrolina, Pernambuco, Brasil',
    descricao: 'A festa de casamento de Alan e Bia, em Petrolina — onde tudo começou.',
    duracaoHoras: 6
  }
};

/* ========================================================================= */

(() => {
  'use strict';

  const raiz = document.documentElement;
  const estatico = raiz.dataset.estatico === '1';
  const semMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const suavizar = !estatico && !semMovimento;

  const $  = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ------------------------------------------------------------------
     Rolagem suave (Lenis) — opcional. Se a biblioteca não carregar,
     o site continua funcionando com a rolagem normal do navegador.
     ------------------------------------------------------------------ */
  let lenis = null;

  function iniciaRolagem() {
    if (!suavizar || typeof window.Lenis !== 'function') return;
    lenis = new window.Lenis({ duration: 1.05, smoothWheel: true, wheelMultiplier: 0.9 });
    const laco = (t) => { lenis.raf(t); requestAnimationFrame(laco); };
    requestAnimationFrame(laco);

    if (window.gsap && window.ScrollTrigger) {
      lenis.on('scroll', window.ScrollTrigger.update);
      window.ScrollTrigger.refresh();
    }
  }

  function irPara(alvo) {
    const el = typeof alvo === 'string' ? $(alvo) : alvo;
    if (!el) return;
    if (lenis) lenis.scrollTo(el, { offset: -70 });
    else el.scrollIntoView({ behavior: semMovimento ? 'auto' : 'smooth', block: 'start' });
  }

  /* ------------------------------------------------------------------
     Navegação: barra fixa, menu do celular, link da seção atual
     ------------------------------------------------------------------ */
  const nav = $('#nav');
  const menu = $('#menu');
  const hamburguer = $('#hamburguer');

  function alternaMenu(abrir) {
    const aberto = abrir ?? menu.dataset.aberto !== 'true';
    menu.dataset.aberto = String(aberto);
    hamburguer.setAttribute('aria-expanded', String(aberto));
    hamburguer.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
    document.body.style.overflow = aberto ? 'hidden' : '';
    if (lenis) aberto ? lenis.stop() : lenis.start();
  }

  hamburguer?.addEventListener('click', () => alternaMenu());
  $$('#menu a').forEach((a) => a.addEventListener('click', () => alternaMenu(false)));

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu?.dataset.aberto === 'true') alternaMenu(false);
  });

  // âncoras internas passam pela rolagem suave
  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const alvo = a.getAttribute('href');
      if (!alvo || alvo === '#' || a.hasAttribute('download')) return;
      const el = $(alvo);
      if (!el) return;
      e.preventDefault();
      irPara(el);
      history.replaceState(null, '', alvo);
    });
  });

  const barra = $('#progresso');
  const linksNav = $$('.nav__links a');
  const secoes = linksNav
    .map((a) => $(a.getAttribute('href')))
    .filter(Boolean);

  function aoRolar() {
    const y = window.scrollY;
    nav?.classList.toggle('nav--fixa', y > window.innerHeight * 0.75);

    if (barra) {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      barra.style.width = `${total > 0 ? Math.min(100, (y / total) * 100) : 0}%`;
    }

    // qual seção está no meio da tela
    const meio = y + window.innerHeight * 0.4;
    let atual = -1;
    secoes.forEach((s, i) => { if (s.offsetTop <= meio) atual = i; });
    linksNav.forEach((a, i) =>
      a.setAttribute('aria-current', i === atual ? 'true' : 'false'));
  }

  window.addEventListener('scroll', aoRolar, { passive: true });
  aoRolar();

  /* ------------------------------------------------------------------
     Revelação dos elementos ao entrar na tela
     ------------------------------------------------------------------ */
  if (estatico || semMovimento || !('IntersectionObserver' in window)) {
    $$('[data-revela]').forEach((el) => el.classList.add('dentro'));
    $$('[data-capitulo]').forEach((el) => el.classList.add('visivel'));
    $$('.mosaico__item').forEach((el) => el.classList.add('dentro'));
  } else {
    const olho = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('dentro');
        olho.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    $$('[data-revela]').forEach((el) => olho.observe(el));

    const olhoCapitulo = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => e.target.classList.toggle('visivel', e.isIntersecting));
    }, { threshold: 0.2, rootMargin: '-10% 0px -30% 0px' });

    $$('[data-capitulo]').forEach((el) => olhoCapitulo.observe(el));
  }

  /* ------------------------------------------------------------------
     Linha da rota que se preenche conforme a rolagem
     ------------------------------------------------------------------ */
  const rota = $('#rota');
  const preenche = $('#rota-preenche');

  function atualizaRota() {
    if (!rota || !preenche) return;
    const r = rota.getBoundingClientRect();
    const alvo = window.innerHeight * 0.55;
    const avanco = (alvo - r.top) / r.height;
    preenche.style.height = `${Math.max(0, Math.min(1, avanco)) * 100}%`;
  }

  if (!estatico && rota) {
    window.addEventListener('scroll', atualizaRota, { passive: true });
    window.addEventListener('resize', atualizaRota);
    atualizaRota();
  } else if (preenche) {
    preenche.style.height = '100%';
  }

  /* ------------------------------------------------------------------
     Contadores de distância (800 km → 150 km → 0 km)
     ------------------------------------------------------------------ */
  $$('[data-conta]').forEach((el) => {
    const de = Number(el.dataset.de);
    const ate = Number(el.dataset.ate);
    if (estatico || semMovimento || !('IntersectionObserver' in window)) {
      el.textContent = String(ate);
      return;
    }
    el.textContent = String(de);
    const obs = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        obs.unobserve(el);
        const inicio = performance.now();
        const dur = 1500;
        const passo = (agora) => {
          const t = Math.min(1, (agora - inicio) / dur);
          const suave = 1 - Math.pow(1 - t, 3);
          el.textContent = String(Math.round(de + (ate - de) * suave));
          if (t < 1) requestAnimationFrame(passo);
        };
        requestAnimationFrame(passo);
      });
    }, { threshold: 0.6 });
    obs.observe(el);
  });

  /* ------------------------------------------------------------------
     Mapa: os pinos acendem em sequência quando o mapa aparece
     ------------------------------------------------------------------ */
  const palco = $('#mapa-palco');
  if (palco) {
    const pinos = $$('.mapa__pino', palco)
      .sort((a, b) => Number(a.dataset.ordem) - Number(b.dataset.ordem));

    if (estatico || semMovimento || !('IntersectionObserver' in window)) {
      pinos.forEach((p) => p.classList.add('acesa'));
    } else {
      const obs = new IntersectionObserver((entradas) => {
        entradas.forEach((e) => {
          if (!e.isIntersecting) return;
          obs.unobserve(palco);
          pinos.forEach((p, i) => setTimeout(() => p.classList.add('acesa'), 400 + i * 520));
        });
      }, { threshold: 0.35 });
      obs.observe(palco);
    }
  }

  /* ------------------------------------------------------------------
     Contagem regressiva
     ------------------------------------------------------------------ */
  const alvoData = CONFIG.dataCasamento;
  const celulas = {
    dias: $('#c-dias'), horas: $('#c-horas'),
    min: $('#c-min'), seg: $('#c-seg')
  };

  function tique() {
    if (!celulas.dias) return;
    const falta = alvoData.getTime() - Date.now();
    if (falta <= 0) {
      celulas.dias.textContent = '0';
      celulas.horas.textContent = '0';
      celulas.min.textContent = '0';
      celulas.seg.textContent = '0';
      return;
    }
    const s = Math.floor(falta / 1000);
    celulas.dias.textContent = String(Math.floor(s / 86400));
    celulas.horas.textContent = String(Math.floor((s % 86400) / 3600));
    celulas.min.textContent = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    celulas.seg.textContent = String(s % 60).padStart(2, '0');
  }
  tique();
  setInterval(tique, 1000);

  /* ------------------------------------------------------------------
     Poeira dourada do hero
     ------------------------------------------------------------------ */
  const tela = $('#poeira');
  if (tela && suavizar) {
    const ctx = tela.getContext('2d');
    let particulas = [];
    let animando = true;

    function dimensiona() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const r = tela.getBoundingClientRect();
      tela.width = r.width * dpr;
      tela.height = r.height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const qtd = Math.min(70, Math.round(r.width / 22));
      particulas = Array.from({ length: qtd }, () => ({
        x: Math.random() * r.width,
        y: Math.random() * r.height,
        r: Math.random() * 1.7 + 0.5,
        vy: -(Math.random() * 0.28 + 0.06),
        vx: (Math.random() - 0.5) * 0.16,
        a: Math.random() * 0.45 + 0.12,
        f: Math.random() * Math.PI * 2
      }));
    }

    function desenha() {
      if (!animando) return;
      const r = tela.getBoundingClientRect();
      ctx.clearRect(0, 0, r.width, r.height);
      particulas.forEach((p) => {
        p.y += p.vy;
        p.x += p.vx + Math.sin((p.f += 0.008)) * 0.14;
        if (p.y < -8) { p.y = r.height + 8; p.x = Math.random() * r.width; }
        if (p.x < -8) p.x = r.width + 8;
        if (p.x > r.width + 8) p.x = -8;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(226, 203, 147, ${p.a})`;
        ctx.fill();
      });
      requestAnimationFrame(desenha);
    }

    dimensiona();
    desenha();
    window.addEventListener('resize', dimensiona);

    // economiza bateria quando o hero sai da tela
    const heroObs = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (e.isIntersecting && !animando) { animando = true; desenha(); }
        else if (!e.isIntersecting) animando = false;
      });
    }, { threshold: 0.02 });
    heroObs.observe(tela);
  }

  /* ------------------------------------------------------------------
     Galeria: monta o mosaico a partir de assets/data/galeria.json
     ------------------------------------------------------------------ */
  const mosaico = $('#mosaico');
  const filtros = $('#filtros');
  const vazio = $('#galeria-vazio');
  let fotos = [];

  async function montaGaleria() {
    if (!mosaico) return;
    // assets/data/galeria.js define window.GALERIA — assim a galeria funciona
    // inclusive abrindo o index.html direto do disco. O fetch fica de reserva.
    if (window.GALERIA && Array.isArray(window.GALERIA.fotos)) {
      fotos = window.GALERIA.fotos;
    } else {
      try {
        const resp = await fetch('assets/data/galeria.json');
        if (!resp.ok) throw new Error(resp.status);
        fotos = (await resp.json()).fotos || [];
      } catch (err) {
        console.warn('Galeria não carregou:', err);
        mosaico.innerHTML =
          '<p class="galeria__vazio">Não consegui carregar as fotos. Rode ' +
          '<code>tools/2_preparar_imagens.py</code> para gerá-las.</p>';
        return;
      }
    }

    if (!fotos.length) {
      mosaico.innerHTML = '<p class="galeria__vazio">Nenhuma foto ainda.</p>';
      return;
    }

    // botões de filtro, na ordem da história
    const capitulos = [];
    fotos.forEach((f) => {
      if (!capitulos.some((c) => c.id === f.capitulo)) {
        capitulos.push({ id: f.capitulo, rotulo: f.rotulo, ordem: f.ordem });
      }
    });
    capitulos.sort((a, b) => a.ordem - b.ordem);

    if (filtros) {
      filtros.innerHTML = '';
      const todos = document.createElement('button');
      todos.type = 'button';
      todos.textContent = `Tudo (${fotos.length})`;
      todos.dataset.filtro = 'tudo';
      todos.setAttribute('aria-pressed', 'true');
      filtros.appendChild(todos);

      capitulos.forEach((c) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = c.rotulo;
        b.dataset.filtro = c.id;
        b.setAttribute('aria-pressed', 'false');
        filtros.appendChild(b);
      });

      filtros.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        $$('button', filtros).forEach((b) =>
          b.setAttribute('aria-pressed', String(b === btn)));
        aplicaFiltro(btn.dataset.filtro);
      });
    }

    mosaico.innerHTML = '';
    fotos.forEach((f, i) => {
      const fig = document.createElement('figure');
      fig.className = 'mosaico__item';
      fig.dataset.capitulo = f.capitulo;
      fig.dataset.indice = String(i);
      fig.innerHTML = `
        <button class="mosaico__botao" type="button" data-abre="${i}">
          <picture>
            <source type="image/webp"
              srcset="assets/img/galeria/${f.id}-700.webp 700w, assets/img/galeria/${f.id}-1400.webp 1400w"
              sizes="(max-width: 620px) 50vw, (max-width: 980px) 33vw, 25vw" />
            <img src="assets/img/galeria/${f.id}-700.jpg" alt="${escapa(f.alt)}"
                 width="700" height="875" loading="lazy" decoding="async" />
          </picture>
          <span class="mosaico__tag">${escapa(f.rotulo)}</span>
          <span class="mosaico__legenda">${escapa(f.legenda)}</span>
        </button>`;
      mosaico.appendChild(fig);
    });

    // entrada escalonada
    if (estatico || semMovimento || !('IntersectionObserver' in window)) {
      $$('.mosaico__item').forEach((el) => el.classList.add('dentro'));
    } else {
      const obs = new IntersectionObserver((entradas) => {
        entradas.forEach((e, k) => {
          if (!e.isIntersecting) return;
          setTimeout(() => e.target.classList.add('dentro'), k * 55);
          obs.unobserve(e.target);
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -5% 0px' });
      $$('.mosaico__item').forEach((el) => obs.observe(el));
    }

    mosaico.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-abre]');
      if (btn) abreLightbox(Number(btn.dataset.abre));
    });
  }

  function aplicaFiltro(filtro) {
    let visiveis = 0;
    $$('.mosaico__item').forEach((el) => {
      const mostra = filtro === 'tudo' || el.dataset.capitulo === filtro;
      el.hidden = !mostra;
      if (mostra) visiveis++;
    });
    if (vazio) vazio.hidden = visiveis > 0;
  }

  function escapa(txt) {
    return String(txt ?? '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* ------------------------------------------------------------------
     Lightbox
     ------------------------------------------------------------------ */
  const lightbox = $('#lightbox');
  const lbImg = lightbox ? $('img', lightbox) : null;
  const lbLegenda = $('#lightbox-legenda');
  const lbContador = $('#lightbox-contador');
  let indiceAtual = 0;
  let ultimoFoco = null;

  function listaVisivel() {
    return $$('.mosaico__item').filter((el) => !el.hidden)
      .map((el) => Number(el.dataset.indice));
  }

  function abreLightbox(indice) {
    if (!lightbox || !fotos.length) return;
    ultimoFoco = document.activeElement;
    indiceAtual = indice;
    pinta();
    lightbox.dataset.aberto = 'true';
    document.body.style.overflow = 'hidden';
    if (lenis) lenis.stop();
    $('.lightbox__fechar', lightbox)?.focus();
  }

  function fechaLightbox() {
    if (!lightbox) return;
    lightbox.dataset.aberto = 'false';
    document.body.style.overflow = '';
    if (lenis) lenis.start();
    ultimoFoco?.focus();
  }

  function pinta() {
    const f = fotos[indiceAtual];
    if (!f || !lbImg) return;
    lbImg.src = `assets/img/galeria/${f.id}-cheia.jpg`;
    lbImg.alt = f.alt || '';
    if (lbLegenda) lbLegenda.textContent = f.legenda || '';
    const lista = listaVisivel();
    const pos = lista.indexOf(indiceAtual);
    if (lbContador) {
      lbContador.textContent = `${f.rotulo} · ${pos + 1} de ${lista.length}`;
    }
  }

  function navega(passo) {
    const lista = listaVisivel();
    if (!lista.length) return;
    const pos = lista.indexOf(indiceAtual);
    indiceAtual = lista[(pos + passo + lista.length) % lista.length];
    pinta();
  }

  if (lightbox) {
    $('.lightbox__fechar', lightbox).addEventListener('click', fechaLightbox);
    $('.lightbox__seta--ant', lightbox).addEventListener('click', () => navega(-1));
    $('.lightbox__seta--prox', lightbox).addEventListener('click', () => navega(1));
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) fechaLightbox();
    });

    document.addEventListener('keydown', (e) => {
      if (lightbox.dataset.aberto !== 'true') return;
      if (e.key === 'Escape') fechaLightbox();
      if (e.key === 'ArrowLeft') navega(-1);
      if (e.key === 'ArrowRight') navega(1);
    });

    // arrastar no celular
    let x0 = null;
    lightbox.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    lightbox.addEventListener('touchend', (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 55) navega(dx < 0 ? 1 : -1);
      x0 = null;
    }, { passive: true });
  }

  /* ------------------------------------------------------------------
     Pop-up de confirmação de presença

     Os botões "Confirmar presença" espalhados pela página abrem este
     pop-up, que mostra o Pix e o endereço antes de mandar o convidado
     para o formulário de verdade.
     ------------------------------------------------------------------ */
  const modal = $('#modal-presenca');
  let focoAntesDoModal = null;

  function focaveis() {
    return $$('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])', modal)
      .filter((el) => el.offsetParent !== null);
  }

  function abreModal(origem) {
    if (!modal) return;
    // guarda quem abriu para devolver o foco no fim. Nao da para confiar no
    // document.activeElement: o Safari nao foca botao ao clicar.
    focoAntesDoModal = origem || document.activeElement;
    modal.dataset.aberto = 'true';
    document.body.style.overflow = 'hidden';
    if (lenis) lenis.stop();
    $('.modal__fechar', modal)?.focus();
  }

  function fechaModal() {
    if (!modal || modal.dataset.aberto !== 'true') return;
    modal.dataset.aberto = 'false';
    document.body.style.overflow = '';
    if (lenis) lenis.start();
    if (focoAntesDoModal && document.contains(focoAntesDoModal)) {
      focoAntesDoModal.focus();
    }
  }

  $$('[data-abre-presenca]').forEach((btn) =>
    btn.addEventListener('click', () => abreModal(btn)));

  if (modal) {
    $('.modal__fechar', modal).addEventListener('click', fechaModal);

    // clicar no fundo escuro fecha
    modal.addEventListener('click', (e) => { if (e.target === modal) fechaModal(); });

    document.addEventListener('keydown', (e) => {
      if (modal.dataset.aberto !== 'true') return;
      if (e.key === 'Escape') { fechaModal(); return; }
      // prende o foco dentro do pop-up enquanto ele estiver aberto
      if (e.key !== 'Tab') return;
      const lista = focaveis();
      if (!lista.length) return;
      const primeiro = lista[0];
      const ultimo = lista[lista.length - 1];
      if (e.shiftKey && document.activeElement === primeiro) {
        e.preventDefault(); ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault(); primeiro.focus();
      }
    });

    // preenche Pix, endereço e link a partir do CONFIG
    const chave = $('#pix-chave');
    if (chave && CONFIG.pix?.chave) {
      chave.textContent = CONFIG.pix.chave;
      $('#btn-copiar-pix')?.setAttribute('data-copiar', CONFIG.pix.chave);
    }
    const rotuloPix = $('.pix__rotulo', modal);
    if (rotuloPix && CONFIG.pix?.rotulo) rotuloPix.textContent = CONFIG.pix.rotulo;

    const endereco = $('#endereco');
    if (endereco && CONFIG.endereco) {
      endereco.innerHTML = `${escapa(CONFIG.endereco.linha1)}<br />${escapa(CONFIG.endereco.linha2)}`;
      $('#btn-copiar-endereco')?.setAttribute(
        'data-copiar', `${CONFIG.endereco.linha1} - ${CONFIG.endereco.linha2}`
          .replace(/ /g, ' '));
    }

    const irFormulario = $('#btn-ir-formulario');
    if (irFormulario) {
      if (CONFIG.linkConfirmacao && !CONFIG.linkConfirmacao.includes('COLOQUE-O-LINK')) {
        irFormulario.href = CONFIG.linkConfirmacao;
      } else {
        // link ainda não configurado: avisa em vez de levar a lugar nenhum
        irFormulario.removeAttribute('target');
        irFormulario.addEventListener('click', (e) => {
          e.preventDefault();
          const nota = $('.modal__nota');
          if (nota) {
            nota.textContent = 'O link do formulário ainda não foi configurado ' +
              '(CONFIG.linkConfirmacao, em js/main.js).';
            nota.style.color = 'var(--oliva)';
          }
        });
      }
    }
  }

  /* ------------------------------------------------------------------
     Botões de copiar (chave Pix e endereço)
     ------------------------------------------------------------------ */
  $$('[data-copiar]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const texto = btn.dataset.copiar;
      const original = btn.innerHTML;
      const avisa = (msg) => {
        btn.textContent = msg;
        btn.dataset.copiado = 'true';
        setTimeout(() => {
          btn.innerHTML = original;
          delete btn.dataset.copiado;
        }, 2200);
      };
      try {
        await navigator.clipboard.writeText(texto);
        avisa(btn.dataset.ok || 'Copiado!');
      } catch {
        // navegador antigo ou sem permissão: mostra para copiar na mão
        window.prompt('Copie aqui:', texto);
      }
    });
  });

  /* ------------------------------------------------------------------
     Botão "salvar na agenda" (.ics gerado na hora)
     ------------------------------------------------------------------ */
  const btnAgenda = $('#btn-agenda');
  if (btnAgenda) {
    const pad = (n) => String(n).padStart(2, '0');
    const paraICS = (d) =>
      `${d.getUTCFullYear()}${pad(d.getUTCMonth() + 1)}${pad(d.getUTCDate())}T` +
      `${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}00Z`;

    const inicio = CONFIG.dataCasamento;
    const fim = new Date(inicio.getTime() + CONFIG.evento.duracaoHoras * 3600 * 1000);

    const ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Alan e Bia//Casamento//PT-BR',
      'CALSCALE:GREGORIAN', 'BEGIN:VEVENT',
      `UID:alan-bia-21-11-2026@casamento`,
      `DTSTAMP:${paraICS(new Date())}`,
      `DTSTART:${paraICS(inicio)}`,
      `DTEND:${paraICS(fim)}`,
      `SUMMARY:${CONFIG.evento.titulo}`,
      `LOCATION:${CONFIG.evento.local}`,
      `DESCRIPTION:${CONFIG.evento.descricao}`,
      'BEGIN:VALARM', 'TRIGGER:-P7D', 'ACTION:DISPLAY',
      'DESCRIPTION:Falta uma semana para o casamento de Alan e Bia!', 'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR'
    ].join('\r\n');

    btnAgenda.href = URL.createObjectURL(new Blob([ics], { type: 'text/calendar;charset=utf-8' }));
  }

  /* ------------------------------------------------------------------
     Sobe tudo
     ------------------------------------------------------------------ */
  iniciaRolagem();
  montaGaleria();

  // acessibilidade: sanfona do FAQ abre uma por vez no desktop
  const sanfona = $('.sanfona');
  if (sanfona && window.matchMedia('(min-width: 861px)').matches) {
    $$('details', sanfona).forEach((d) => {
      d.addEventListener('toggle', () => {
        if (!d.open) return;
        $$('details', sanfona).forEach((o) => { if (o !== d) o.open = false; });
      });
    });
  }
})();
