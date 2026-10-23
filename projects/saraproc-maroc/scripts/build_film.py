#!/usr/bin/env python3
"""Assemble the editable chapter fragments into the standalone HyperFrames film."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
bridges=[(18,20),(42,44),(58,60),(74,76),(90,92),(106,108),(124,126),(150,152),(164,166),(178,180),(192,194),(208,210)]
parts=[]
for path in sorted((ROOT/'beats').glob('*.html')):
    parts.append(path.read_text())
for i,(start,end) in enumerate(bridges):
    parts.append(f'''<section id="bridge-{i+1:02}" class="scene chapter-bridge" data-t0="{start}" data-t1="{end}">
    <div class="scene-content">
      <img class="logo reveal" src="assets/logo-supplied-2.png" alt="Les laboratoires SARAPROC d’hygiène professionnelle">
      <p class="bridge-line reveal">Les laboratoires SARAPROC</p>
    </div></section>''')
parts.append('''<section id="official-finale" class="scene dark outro" data-t0="220" data-t1="225">
  <div class="scene-content">
    <img class="logo reveal" src="assets/logo-footer.png" alt="Logo officiel SARAPROC MAROC">
    <h2 class="wide-title reveal">SARAPROC MAROC</h2>
    <p class="website reveal">saraprocmaroc.com</p>
  </div></section>''')
# Fragments contain only section scenes and optional scoped styles.
sections=[]
styles=[]
for part in parts:
    styles+=re.findall(r'<style[^>]*>(.*?)</style>',part,re.S)
    sections+=re.findall(r'<section\b.*?</section>',part,re.S)
sections.sort(key=lambda s:float(re.search(r'data-t0="([\d.]+)"',s).group(1)))
previous=0
for section in sections:
    start=float(re.search(r'data-t0="([\d.]+)"',section).group(1))
    end=float(re.search(r'data-t1="([\d.]+)"',section).group(1))
    if start!=previous or end<=start:raise ValueError(f'Timeline gap/overlap at {start}; previous end={previous}')
    previous=end
if previous!=225:raise ValueError(f'Timeline ends at {previous}, expected 225')
for i,section in enumerate(sections):
    # Media gets its real active interval, including the outgoing crossfade.
    # This also prevents repeated logo assets being discovered at one default time.
    start=float(re.search(r'data-t0="([\d.]+)"',section).group(1))
    end=float(re.search(r'data-t1="([\d.]+)"',section).group(1))
    span=min(225,end+.6)-start
    scene_id=re.search(r'<section\s+id="([^"]+)"',section).group(1)
    media_count=[0]
    def tag_media(match):
        media_count[0]+=1
        return f'<img id="{scene_id}-media-{media_count[0]}" data-start="{start:g}" data-duration="{span:g}" data-track-index="{100+i*10+media_count[0]}"'
    section=re.sub(r'<img\b',tag_media,section)
    section=section.replace('class="photo drift"','class="photo drift" data-layout-allow-overflow')
    if 'class="photo drift"' not in section and 'chapter-bridge' not in section:
        # These editorial cards intentionally hold still so the audience can read.
        section=section.replace('class="scene ', 'data-hold class="scene ',1)
    if i in [0,len(sections)-1]:
        section=section.replace('<div class="scene-content">','<div class="ambient" aria-hidden="true" data-layout-ignore></div><div class="scene-content">',1)
    sections[i]=section
html='''<!doctype html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<title>SARAPROC MAROC — Présentation</title>
<script src="vendor/gsap.min.js"></script>
<link rel="stylesheet" href="film.css">
<style>'''+ '\n'.join(styles)+'''</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="225" data-width="1920" data-height="1080" data-fps="30">
'''+ '\n'.join(sections)+'''
<audio id="original-score" src="assets/music-original.m4a" data-start="0" data-duration="225" data-track-index="3" data-volume="1"></audio>
</div><script>'''+(ROOT/'film.js').read_text()+'''</script></body></html>'''
(ROOT/'index.html').write_text(html)
print(f'Built {len(sections)} scenes, 225s, 1920x1080 at 30 fps')
