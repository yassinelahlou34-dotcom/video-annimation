# Original soundtrack — SARAPROC MAROC

This instrumental score was composed for this presentation from an original
note sequence and arrangement. Its piano-like keys, plucks, pads, bass and drums
are generated mathematically by `../scripts/compose_music.py`.

No recordings, soundfonts, commercial tracks, Epidemic Sound downloads, vocals,
or third-party musical samples are included. NumPy and SciPy process the signal;
FFmpeg masters and encodes it. The generated percussion is part of the music,
not added sound effects.

You may use and edit the generated soundtrack with this presentation. No music
subscription or track attribution is required by this project. This statement
describes the track's provenance; it does not promise exclusivity over common
chords, conventional musical patterns, or synthetic instrument timbres.

## Production

- Tempo: 120 BPM; key centre: D major; duration: 225 seconds.
- Stereo, 48 kHz PCM WAV plus AAC/M4A delivery copy.
- Original four-chord voicings, alternating arpeggio patterns, sparse melodic
  phrases, section-dependent energy, and a final D-major resolution.
- The score contains 0.75-second silence windows immediately before the section
  entry times in `../scripts/pauses.json`, with short ramp-down/ramp-up envelopes.
- No voiceover.

Rebuild from the project directory:

```bash
python3 scripts/compose_music.py --pause-file scripts/pauses.json
```

Requires Python 3 with NumPy and SciPy, and FFmpeg. The script is deterministic
and performs a two-pass loudness master before inserting exact silence gaps.
`music-report.json` records duration, peak level, clipping and silence checks.
