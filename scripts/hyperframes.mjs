import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';

const require = createRequire(import.meta.url);
const manifestPath = require.resolve('hyperframes/package.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const bin = typeof manifest.bin === 'string' ? manifest.bin : manifest.bin.hyperframes;
const result = spawnSync(process.execPath, [resolve(dirname(manifestPath), bin), ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: {
    ...process.env, HYPERFRAMES_NO_TELEMETRY: '1', HYPERFRAMES_SKIP_SKILLS: '1',
    XDG_STATE_HOME: process.env.XDG_STATE_HOME || resolve(dirname(fileURLToPath(import.meta.url)), '../.cache/state'),
    ...(process.env.HYPERFRAMES_BROWSER_PATH ? {} : existsSync('/usr/bin/chromium')
      ? { HYPERFRAMES_BROWSER_PATH: '/usr/bin/chromium' } : {})
  }
});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
