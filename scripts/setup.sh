#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for tool in node npm python3 ffmpeg ffprobe; do
  command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 1; }
done
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) { console.error("Node.js 22+ required"); process.exit(1); }'
node -e 'const fs=require("node:fs"),os=require("node:os"),p=require("node:path"); for(const dir of [".cache/hyperframes",".hyperframes"]) fs.mkdirSync(p.join(os.homedir(),dir),{recursive:true});'
npm ci
npm run doctor
