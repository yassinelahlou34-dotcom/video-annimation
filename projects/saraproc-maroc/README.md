# SARAPROC MAROC — présentation

Film français de 3 min 45 s, 1920 × 1080, 30 images/s. Treize chapitres dans l’ordre
du brief, transitions avec le logo laboratoire fourni, musique instrumentale
originale et aucune voix off. Le dernier plan utilise le logo officiel blanc
du site, distinct des deux logos du PDF.

Depuis la racine du dépôt :

```bash
npm ci
npm run studio -- saraproc-maroc
npm run check -- saraproc-maroc
npm run render -- saraproc-maroc --quality high --fps 30
```

Le rendu est écrit dans `exports/saraproc-maroc.mp4`. Un nouveau rendu peut
remplacer ce fichier ; sauvegardez les versions que vous souhaitez conserver.

## Modifier le film

1. Modifiez les chapitres HTML dans `beats/`, la présentation dans `film.css`,
   et la chorégraphie dans `film.js`. Respectez `DESIGN.md` et les identités fournies.
2. Reconstruisez le fichier `index.html` :

   ```bash
   python3 projects/saraproc-maroc/scripts/build_film.py
   ```

3. Lancez les vérifications, puis examinez les images avec HyperFrames :

   ```bash
   npm run check -- saraproc-maroc
   npm run hf -- snapshot projects/saraproc-maroc --at 4,25,48,80,130,183,215,223.5
   ```

4. Relancez le rendu après vos modifications.

`index.html` est un fichier assemblé. Les 13 fragments éditables dans `beats/`
restent la source du contenu ; ne modifiez pas uniquement le fichier assemblé.
Son avertissement de longueur dans le linter correspond à cet assemblage de 39
plans et transitions. Les photographies ont un zoom discret dans leurs cadres ;
les logos ne sont ni recadrés, ni recolorés, ni redessinés. Les cartes de lecture
sans photographie gardent volontairement le texte stable.

Le contrôle peut signaler un contraste faible du texte sortant pendant les
fondus. Les contrôles de contenu sont également exécutés au milieu des plans,
après les animations d’entrée. Les textes sont lisibles sur leurs fonds pleins.

## Musique

`assets/music-original.m4a` est la piste utilisée et versionnée dans Git. Le master
WAV peut être reconstruit avec le script de composition fourni ; il reste également
dans l’archive éditable de cette machine. Douze silences de 0,75 seconde se terminent aux entrées
des secteurs : 20, 44, 60, 76, 92, 108, 126, 152, 166, 180, 194 et 210 secondes.
Le tempo est de 120 BPM. La résolution finale accompagne le logo à 220–225 s.

Pour recomposer la musique, Python doit disposer de NumPy et SciPy. Ils sont déjà
présents dans cette machine. Versions utilisées : `scripts/music-requirements.txt`.
Depuis ce dossier :

```bash
python3 scripts/compose_music.py --pause-file scripts/pauses.json
```

Le script est déterministe et utilise FFmpeg pour le mastering. Voir
`assets/MUSIC-LICENSE.md` et `assets/music-report.json` pour la provenance et les
mesures. Aucun morceau Epidemic Sound, échantillon musical tiers ou abonnement
n’est utilisé.

## Sources et originaux

- `BRIEF.txt` : votre brief original.
- `assets/logos-original.pdf` : le PDF fourni, conservé.
- `research/` et `SOURCE-MAP.md` : références du site et décisions factuelles.
- `SCRIPT.md` : texte à l’écran, dans l’ordre chronologique.
- `STORYBOARD.md` : minutage et direction du film.
- `snapshots-final/` : images de revue locales, non versionnées dans Git.

La capture automatisée du site a échoué. Les textes et photographies utilisés
ont été récupérés directement par HTTPS avec vérification TLS, puis conservés
localement. Le film et ses animations ne dépendent pas du site en direct.
