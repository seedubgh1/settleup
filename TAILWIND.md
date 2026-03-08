# Tailwind CSS Build

Tailwind is compiled locally — the CDN is not used. The compiled output is
`static/css/main.css` and is committed to the repo.

## Prerequisites

Node.js is managed via nvm. If `npm` is not found, load nvm first:

```bash
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"
```

To make this permanent, add those two lines to your `~/.bashrc`.

---

## One-time build (production / before deploying)

```bash
npm run build:css
```

Scans all `templates/**/*.html` and `static/**/*.js` files, then writes a
minified `static/css/main.css`. Run this before every deployment.

---

## Watch mode (during development)

```bash
npm run watch:css
```

Runs continuously in a terminal. Automatically rebuilds `main.css` whenever
you save a template file. Press **Ctrl+C** to stop.

> **Important:** if you add a new Tailwind utility class to a template and the
> styling doesn't appear, either watch mode isn't running or you need to do a
> manual `npm run build:css`.

---

## Theme / custom values

Custom colors and fonts are defined in `static/css/input.css` inside the
`@theme` block. Edit that file to change or extend the design tokens, then
rebuild.

| Token | Value |
|---|---|
| `surface` | `#0f1117` (page background) |
| `surface-raised` | `#161b27` (card background) |
| `surface-border` | `#1e2535` (border color) |
| `accent` | `#4ade80` (green highlight) |
| `ink` | `#f1f5f9` (primary text) |
| `ink-muted` | `#94a3b8` (secondary text) |
