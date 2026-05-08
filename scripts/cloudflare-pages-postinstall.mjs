import { rmSync } from 'node:fs';
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

console.log('Cloudflare Pages detected. Rebuilding Astro output for web/dist...');

rmSync('web/dist', { recursive: true, force: true });

const nodeCommand = process.execPath;
const result = spawnSync(nodeCommand, ['scripts/build-web.mjs'], {
  stdio: 'inherit',
  shell: false,
  env: {
    ...process.env,
    ASTRO_TELEMETRY_DISABLED: '1',
  },
});

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
