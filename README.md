# Video editing workspace

[Download the SARAPROC MAROC video — Full HD, 3:45](deliverables/saraproc-maroc.mp4?raw=1)

The rendered H.264/AAC MP4 is included in `deliverables/`. If GitHub does not show
an inline player, use its raw/download action to save the video and open it locally.

HyperFrames authors HTML/CSS/GSAP animations and supplies Studio preview and rendering.
FFmpeg handles trimming, conversion and audio mixing. This is an agent-assisted,
command-driven workspace; send your video prompt when you are ready to create content.
The SARAPROC MAROC presentation lives in `projects/saraproc-maroc/`; its editable
chapters, source references, logo assets and original soundtrack are included.
See that project's `README.md` for editing and rebuilding it.

## 1. Prepare the tools

This cloud machine already has Node.js 24, Python 3, FFmpeg 7 and Chromium installed.
The project pins HyperFrames 0.8.188 and GSAP 3.14.2 in `package-lock.json`.

```bash
cd /workspace/video-annimation
bash scripts/setup.sh
npm test
```

On a separate computer, first install Node.js 22+, Python 3, FFmpeg (including
ffprobe), and Chrome/Chromium. Run the commands from your local checkout instead.
The shell setup script targets Linux/macOS (or WSL on Windows). If Chrome is not
detected, set `HYPERFRAMES_BROWSER_PATH` to its actual executable path.

The wrapper opts out of HyperFrames telemetry, uses the existing Chromium on Linux,
and keeps preview state inside the workspace. AI skills are supplied by the installed
HyperFrames plugin; the wrapper prevents the CLI from installing another copy.

## 2. Create a project when you have a video brief

```bash
npm run new -- my-video
```

This scaffolds `projects/my-video/` using the official blank template and copies the
pinned GSAP library into `projects/my-video/vendor/`. New projects therefore do not
need a browser connection to a GSAP CDN. The blank template is a placeholder, not a
completed video. Supply your prompt, duration, aspect ratio, text, style and media
to the agent to author its HTML, CSS and timeline. For vertical video:

```bash
npm run new -- my-short --resolution portrait
```

## 3. Add footage and music

Keep source files in `assets/video/`, `assets/music/` and `assets/voice/`.
These media folders and `exports/` are ignored by Git. Keep backups of originals.
Copy media used inside a composition into that project's `assets/` folder and use
project-relative paths. Shared root assets are for the FFmpeg commands; the preview
server serves the selected project, not arbitrary parent directories.

Epidemic Sound's official pricing FAQ offers a **free trial**, not an ongoing free
plan: <https://www.epidemicsound.com/pricing/>. Sign up on their site if you want
the trial, review the current billing and licensing terms, and download eligible
tracks through your account. Confirm coverage for your channel and publication
date. A downloaded file alone does not establish a publishing license.

For a free music source, consider <https://pixabay.com/music/> and read its current
content license and each track's conditions. YouTube Audio Library is another
option; check attribution and permitted uses for the selected track. This system
imports local audio files; it does not include an Epidemic Sound subscription,
catalog download integration or account credentials.

Record the source and license in `assets/music/LICENSES.csv`. Keep any license
certificate with your own project records. No paid music is bundled.

## 4. Inspect or trim a clip

Replace these example filenames with files you have added:

```bash
npm run media -- probe assets/video/source.mp4
npm run media -- trim assets/video/source.mp4 exports/clip.mp4 --start 2 --duration 8
```

Trim outputs browser-friendly H.264 video and AAC audio when the source has audio.
The media tools reject existing output files and invalid time ranges.

## 5. Validate and open Studio

```bash
npm run check -- my-video
npm run studio -- my-video
```

The check covers lint, browser runtime, layout, motion and contrast. Review warnings;
the untouched blank template may warn that nothing moves. Studio normally uses
port 3002; use `npm run studio -- my-video --port 3010` if it is occupied. Keep the
terminal running and stop it with Ctrl+C. On your own computer, open the Studio
address printed by the CLI. This cloud onboarding UI does not expose a web preview;
browser launch and local HTTP responses can still be tested internally.

For an agent-managed background preview, use:

```bash
npm run hf -- preview projects/my-video --background --no-open
npm run hf -- preview projects/my-video --status
npm run hf -- preview projects/my-video --stop
```

## 6. Export the animation

```bash
npm run render -- my-video
```

Output: `exports/my-video.mp4`. Rendering uses two browser workers and draft quality
for iteration. Rendering again to the same path may replace that render. For final
delivery, use a separate output filename:

```bash
npm run render -- my-video --quality high --fps 30 --output /workspace/video-annimation/exports/my-video-final.mp4
```

## 7. Add licensed background music

```bash
npm run media -- music exports/my-video.mp4 assets/music/track.mp3 exports/my-video-music.mp4 --gain-db -20
```

This preserves existing narration/audio, loops short music to the video length,
adds fades, and reduces music level. It copies the video stream without re-encoding.
Use an H.264 MP4 from the render/trim commands. Listen to the result and adjust
`--gain-db`; this is a fixed-level mix, not automatic speech ducking. If music is
already in the HyperFrames timeline, do not mix it a second time here.

## Optional later additions

Automatic speech transcription, generated voices and generated music are not
installed. `npm run doctor` lists them as optional missing tools. They can be set
up when your video brief needs them; no API key is needed for the core workflow.

The cloud environment saves installed files, but running preview processes must
be started again in a new task. Existing checkouts are already isolated; do not
create a Git worktree unless explicitly requested.
