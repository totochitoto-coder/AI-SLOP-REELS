// Usage: node render.mjs <script.json> <out.mp4> [--fps 30] [--preview]
// Renders the flat_explainer template frame-by-frame with Playwright and pipes frames to ffmpeg.
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const scriptPath = resolve(args[0] || 'scripts/sample_shenzhen.json');
const outPath = resolve(args[1] || 'out/sample.mp4');
const fps = Number(args[args.indexOf('--fps') + 1]) || 30;
const preview = args.includes('--preview');
const here = dirname(new URL(import.meta.url).pathname);
const script = JSON.parse(readFileSync(scriptPath, 'utf8'));
mkdirSync(dirname(outPath), { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 720, height: 1280 } });
await page.goto(pathToFileURL(resolve(here, 'templates/flat_explainer/index.html')).href);
await page.evaluate(() => document.fonts.ready);
const total = await page.evaluate(s => window.setScript(s), script);

if (preview) {
  // contact sheet: one frame per scene at 70% of its duration
  for (const [i, sc] of script.scenes.entries()) {
    const start = script.scenes.slice(0, i).reduce((a, s) => a + s.dur, 0);
    await page.evaluate(t => window.renderFrame(t), start + sc.dur * 0.7);
    await page.screenshot({ path: outPath.replace(/\.mp4$/, `_scene${i + 1}.jpg`), type: 'jpeg', quality: 85 });
  }
  await browser.close();
  process.exit(0);
}

const silent = outPath.replace(/\.mp4$/, '_silent.mp4');
const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '20', silent], { stdio: ['pipe', 'inherit', 'inherit'] });

const frames = Math.ceil(total * fps);
for (let i = 0; i < frames; i++) {
  await page.evaluate(t => window.renderFrame(t), i / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 150 === 0) process.stdout.write(`frame ${i}/${frames}\n`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();

// audio bed + sfx, then mux
const wav = outPath.replace(/\.mp4$/, '.wav');
execFileSync('python3', ['-I', resolve(here, 'audio.py'), scriptPath, wav], { stdio: 'inherit' });
const vi = args.indexOf('--voice');
if (vi >= 0) {
  // voice on top, music ducked underneath it
  const filter = '[1:a]volume=0.45[m];[2:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[md];'
    + '[md][v]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]';
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', silent, '-i', wav, '-i', resolve(args[vi + 1]), '-filter_complex', filter,
    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', outPath], { stdio: 'inherit' });
} else {
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', outPath], { stdio: 'inherit' });
}
console.log(`done: ${outPath} (${total.toFixed(1)}s)`);
