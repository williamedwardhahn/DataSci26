/* ---------------------------------------------------------------------------
   DataSci26 — shared behaviour for the interactive labs.

   Small on purpose: a theme switch, the masthead, and one image loader that
   every lab shares so the sample pictures live in one place and work offline.
   --------------------------------------------------------------------------- */

const Lab = (() => {
  'use strict';

  const KEY = 'datasci26-theme';
  const root = document.documentElement;

  /* -- theme ------------------------------------------------------------- */

  function stored() {
    try { return localStorage.getItem(KEY); } catch { return null; }
  }

  function setTheme(mode) {
    if (mode === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', mode);
    try {
      if (mode === 'system') localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, mode);
    } catch { /* private browsing: the choice just does not persist */ }
    document.querySelectorAll('.theme-switch button').forEach(b =>
      b.setAttribute('aria-pressed', String(b.dataset.theme === mode)));
  }

  function initTheme() {
    const mode = stored() || 'system';
    if (mode !== 'system') root.setAttribute('data-theme', mode);
    return mode;
  }

  /* -- masthead ---------------------------------------------------------- */

  /**
   * Build the plate masthead. `opts.no` is the plate number shown in the rule,
   * `opts.title` the lab name, `opts.back` where the back link points.
   */
  function head({ no, title, back = 'index.html' }) {
    const mode = initTheme();
    const el = document.createElement('header');
    el.className = 'plate-head';
    el.innerHTML = `
      <div class="plate-head__inner">
        <span class="plate-no">${no}</span>
        <h1>${title}</h1>
        <span class="plate-head__spacer"></span>
        <a class="plate-back" href="${back}">&larr; all labs</a>
        <div class="theme-switch" role="group" aria-label="Colour theme">
          <button type="button" data-theme="light">Light</button>
          <button type="button" data-theme="system">Auto</button>
          <button type="button" data-theme="dark">Dark</button>
        </div>
      </div>`;
    document.body.prepend(el);
    el.querySelectorAll('.theme-switch button').forEach(b => {
      b.setAttribute('aria-pressed', String(b.dataset.theme === mode));
      b.addEventListener('click', () => setTheme(b.dataset.theme));
    });
    return el;
  }

  function foot(extra = '') {
    const el = document.createElement('footer');
    el.className = 'plate-foot';
    el.innerHTML = `
      <span>Mathematics of Data Science &middot; DataSci26</span>
      <span><a href="img/CREDITS.md">Sample images</a>: NASA public domain and CC0, via scikit-image</span>
      ${extra}`;
    document.body.append(el);
    return el;
  }

  /* -- sample images ----------------------------------------------------- */

  /* Bundled beside these pages so the labs work offline and cannot rot. */
  const SAMPLES = {
    portrait:  { src: 'img/portrait.jpg',  label: 'Portrait (astronaut)' },
    texture:   { src: 'img/texture.jpg',   label: 'Texture (fur)' },
    colour:    { src: 'img/colour.jpg',    label: 'Colour (coffee cup)' },
    edges:     { src: 'img/edges.jpg',     label: 'Edges (cameraman)' },
    structure: { src: 'img/structure.jpg', label: 'Structure (rocket)' },
  };

  /** A drawn stand-in so a lab still works if an image cannot be fetched. */
  function fallbackImage(w = 512, h = 512) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const g = c.getContext('2d');
    g.fillStyle = '#8a8f98'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 16) {
      for (let x = 0; x < w; x += 16) {
        const v = 90 + 70 * Math.sin(x / 42) * Math.cos(y / 37);
        g.fillStyle = `rgb(${v | 0},${(v * 0.92) | 0},${(v * 0.8) | 0})`;
        g.fillRect(x, y, 16, 16);
      }
    }
    g.fillStyle = '#1b1b1b';
    g.beginPath(); g.arc(w * 0.5, h * 0.5, Math.min(w, h) * 0.22, 0, 7); g.fill();
    return c;
  }

  /**
   * Load a sample by key, a URL, or a File. Always resolves — on failure you
   * get the drawn stand-in rather than a broken lab.
   */
  function loadImage(what) {
    return new Promise(resolve => {
      const done = img => resolve(img);
      if (what instanceof File) {
        const fr = new FileReader();
        fr.onload = () => { const i = new Image(); i.onload = () => done(i); i.onerror = () => done(fallbackImage()); i.src = fr.result; };
        fr.onerror = () => done(fallbackImage());
        fr.readAsDataURL(what);
        return;
      }
      const src = SAMPLES[what] ? SAMPLES[what].src : what;
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => done(img);
      img.onerror = () => done(fallbackImage());
      img.src = src;
    });
  }

  /** <select> of the bundled samples, ready to append. */
  function sampleSelect(id, selected = 'portrait') {
    const s = document.createElement('select');
    s.id = id;
    for (const [k, v] of Object.entries(SAMPLES)) {
      const o = document.createElement('option');
      o.value = k; o.textContent = v.label; o.selected = k === selected;
      s.append(o);
    }
    return s;
  }

  /* -- small helpers ----------------------------------------------------- */

  const $  = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

  /** Fit an image into w x h and return its ImageData. */
  function imageData(img, w, h) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0, w, h);
    return g.getImageData(0, 0, w, h);
  }

  /** Bind a range input to a live value readout. */
  function bindRange(input, out, format = v => v) {
    const show = () => { if (out) out.textContent = format(input.value); };
    input.addEventListener('input', show);
    show();
    return show;
  }

  return { head, foot, setTheme, initTheme, SAMPLES, loadImage, sampleSelect,
           fallbackImage, imageData, bindRange, $, $$, clamp };
})();
