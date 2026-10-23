#!/usr/bin/env python3
"""Small, non-destructive FFmpeg tools. Run with --help for examples."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys


def probe(path):
    if not Path(path).is_file():
        raise ValueError(f"Input does not exist: {path}")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def duration(info):
    value = float(info["format"]["duration"])
    if not math.isfinite(value) or value <= 0:
        raise ValueError("Media must have a finite, positive duration")
    return value


def has_stream(info, kind):
    return any(s["codec_type"] == kind for s in info["streams"])


def output_path(path, inputs):
    target = Path(path).resolve()
    if target in [Path(p).resolve() for p in inputs] or target.exists():
        raise ValueError(f"Refusing to overwrite an existing file: {target}")
    if target.suffix.lower() != ".mp4":
        raise ValueError("Use an .mp4 output filename")
    target.parent.mkdir(parents=True, exist_ok=True)
    return str(target)


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", *args], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("probe", help="Show media metadata")
    inspect.add_argument("input")
    trim = commands.add_parser("trim", help="Cut and encode a clip as browser-friendly H.264/AAC")
    trim.add_argument("input")
    trim.add_argument("output")
    trim.add_argument("--start", type=float, default=0)
    trim.add_argument("--duration", type=float, required=True)
    mix = commands.add_parser("music", help="Mix licensed music under existing audio; loop and fade to video length")
    mix.add_argument("input", help="Video file")
    mix.add_argument("music", help="Audio file you are licensed to use")
    mix.add_argument("output")
    mix.add_argument("--gain-db", type=float, default=-20, help="Music gain, -60 to 0 dB (default -20)")
    args = parser.parse_args()
    info = probe(args.input)
    if args.command == "probe":
        print(json.dumps(info, indent=2))
        return
    length = duration(info)
    if not has_stream(info, "video"):
        raise ValueError("The input must contain a video stream")
    if args.command == "trim":
        if (not all(math.isfinite(v) for v in [args.start, args.duration])
                or args.start < 0 or args.duration <= 0 or args.start + args.duration > length + 0.05):
            raise ValueError(f"Choose a positive duration and a range within the {length:.3f}s input")
        target = output_path(args.output, [args.input])
        ffmpeg(["-ss", str(args.start), "-i", args.input, "-t", str(args.duration),
                "-map", "0:v:0", "-map", "0:a:0?", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1",
                "-c:v", "libx264", "-threads", "2", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", target])
    else:
        if not math.isfinite(args.gain_db) or not -60 <= args.gain_db <= 0:
            raise ValueError("Music gain must be between -60 and 0 dB")
        music = probe(args.music)
        if not has_stream(music, "audio"):
            raise ValueError("Music file has no audio stream")
        duration(music)
        target = output_path(args.output, [args.input, args.music])
        fade = min(1.5, length / 3)
        filters = (f"[1:a:0]atrim=duration={length},asetpts=PTS-STARTPTS,volume={args.gain_db}dB,"
                   f"afade=t=in:st=0:d={fade},afade=t=out:st={length-fade}:d={fade}[music];")
        if has_stream(info, "audio"):
            filters += ("[0:a:0]asetpts=PTS-STARTPTS[original];"
                        "[original][music]amix=inputs=2:duration=longest:normalize=0,"
                        "alimiter=limit=0.95:level=false:latency=true[out]")
        else:
            filters += "[music]alimiter=limit=0.95:level=false:latency=true[out]"
        ffmpeg(["-i", args.input, "-stream_loop", "-1", "-i", args.music,
                "-filter_complex_threads", "2", "-filter_complex", filters,
                "-map", "0:v:0", "-map", "[out]", "-t", str(length),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", target])
    print(f"Created {target}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
