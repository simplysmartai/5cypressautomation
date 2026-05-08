import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const isCloudflarePages =
  process.env.CF_PAGES === '1' ||
  Boolean(process.env.CF_PAGES_BRANCH) ||
  Boolean(process.env.CF_PAGES_COMMIT_SHA) ||
  Boolean(process.env.CF_PAGES_URL);

if (!isCloudflarePages) {
  console.log('Skipping Cloudflare Pages postinstall build outside Cloudflare.');
  process.exit(0);
}

if (existsSync('web/dist/index.html')) {
  console.log('Cloudflare Pages build output already exists. Skipping postinstall build.');
  process.exit(0);
}

console.log('Cloudflare Pages detected. Building Astro output for web/dist...');

const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const result = spawnSync(npmCommand, ['run', 'build'], {
  stdio: 'inherit',
  shell: false,
});

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
