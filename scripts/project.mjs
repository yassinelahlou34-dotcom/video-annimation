import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, copyFileSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [command, name, ...options] = process.argv.slice(2);
if (!['new', 'studio', 'check', 'render'].includes(command) || !name || !/^[a-z0-9][a-z0-9-]*$/.test(name)) {
  console.error('Usage: npm run <new|studio|check|render> -- <project-name> [HyperFrames options]');
  console.error('Use lowercase letters, digits and hyphens for project-name.');
  process.exit(1);
}
const project = resolve(root, 'projects', name);
function run(args) {
  const result = spawnSync(process.execPath, [resolve(root, 'scripts/hyperframes.mjs'), ...args], {
    cwd: root, stdio: 'inherit'
  });
  if (result.error) console.error(result.error.message);
  if (result.status !== 0) process.exit(result.status ?? 1);
}
if (command === 'new') {
  if (existsSync(project)) {
    console.error(`Project already exists: ${project}`);
    process.exit(1);
  }
  mkdirSync(resolve(root, 'projects'), { recursive: true });
  run(['init', project, '--example', 'blank', '--non-interactive', ...options]);
  const require = createRequire(import.meta.url);
  const vendor = resolve(project, 'vendor');
  mkdirSync(vendor, { recursive: true });
  copyFileSync(require.resolve('gsap/dist/gsap.min.js'), resolve(vendor, 'gsap.min.js'));
  const entry = resolve(project, 'index.html');
  writeFileSync(entry, readFileSync(entry, 'utf8').replace(
    'https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js', './vendor/gsap.min.js'));
} else {
  if (!existsSync(resolve(project, 'index.html'))) {
    console.error(`Create the project first: npm run new -- ${name}`);
    process.exit(1);
  }
  if (command === 'studio') run(['preview', project, '--foreground', '--no-open', ...options]);
  if (command === 'check') {
    run(['check', project, ...options]);
  }
  if (command === 'render') {
    mkdirSync(resolve(root, 'exports'), { recursive: true });
    run(['render', project, '--workers', '2', '--quality', 'draft',
      '--output', resolve(root, 'exports', `${name}.mp4`), ...options]);
  }
}
