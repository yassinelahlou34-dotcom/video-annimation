# Composition assembly contract

The root agent assembles HTML fragments in `beats/` into one standalone index.html.
Read DESIGN.md, BRIEF.txt and relevant research/*.json first. No invented facts.
User requests no voiceover. Create markup, not standalone pages or scripts.

Every scene: `<section id="unique-id" class="scene light" data-t0="20" data-t1="30"><div class="scene-content">...</div></section>`.
Use class `dark` instead of `light` for navy. Scene duration endpoints are supplied.
No `data-start`, `data-duration`, `clip` classes, scripts, GSAP, external fonts or
inline SVG in fragments. Root handles every entrance, transition and registration.

Shared CSS classes available:
- `scene-content`: full 1920x1080, padding 92px 104px, flex column gap 28px.
- `split`: a child grid, 2 equal columns, gap 64px, flex:1, align-items:center.
- `copy`: flex column, gap 26px. `kicker reveal` (24px uppercase), `title reveal`
  (82px/1.07, weight 800), `body reveal` (32px/1.4).
- `list`: flex column gap 18px. Each `item reveal` is 31px with a subtle top rule
  and 16px top padding. Max 4 items per split scene, max ~8 words per item.
- `visual reveal`: 780x640 max-width:100%, rounded 28px, overflow hidden; child
  `<img class="photo drift" src="assets/...webp" alt="...">` fills it with object-fit:cover.
- `visual portrait reveal`: same size but object-fit:contain with white background
  for images with logos already in them; no filters or cropping on such images.
- `logo reveal`: img object-fit:contain; set width and max-height inline if needed.
  Never use photo/drift on logos. Available unchanged assets: logo-supplied-1.png
  (medical), logo-supplied-2.png (industrial/lab), logo-official.png (site header),
  logo-footer.png (official white brand mark). Medical width 650, industrial width
  300, use a white `brand-panel reveal` wrapper for logos on dark canvas.
- `tile-grid`: grid 2 columns, gap 28px, flex:1. `tile reveal` white/silver panel
  with 32px padding. Tile h3 36px, p 27px. `tile-grid three` uses 3 columns.
- `wide-title reveal`: 96px, max-width:1600. `large-year reveal`: 210px/1, blue.
- `footer-note reveal`: 24px; factual supporting text. Avoid footnotes on screen.
- `tagline reveal`: 46px/1.3 weight 500. `rule reveal`: 100px wide 4px royal blue.
- `.header-row`: flex horizontal space-between for section title + small logo.

Add `reveal` on each visual/text unit. Parent reveal handles compound cards; do not
reveal both parent and every child. Root uses varying entrance patterns and 0.12s
stagger, plus subtle image zoom only on `drift` children. CSS end-state must already
be correct. Do not position content absolutely; flex/grid inside full scene-content.
If unique styles are necessary, put a scoped <style> in your fragment using your
scene IDs, and respect the palette. Source asset manifest: research/asset-manifest.json.
Mark ornaments `data-layout-ignore`. Do not mark actual content to hide overflow.

13 chapters occupy 0–220s; root supplies 2s laboratory-logo bridges between them
and the official 220–225s finale. No chapter may consume a bridge interval.
Save a short source/copy note alongside your fragment (same name .md).
