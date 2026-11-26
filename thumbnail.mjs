// Usage: node thumbnail.mjs <script.json> <out.png>   (1080x1920 cover from the script's "thumbnail" block)
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const { chromium } = createRequire(import.meta.url)('playwright');
const [scriptPath, out] = process.argv.slice(2);
const S = JSON.parse(readFileSync(scriptPath, 'utf8'));
const here = dirname(new URL(import.meta.url).pathname);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto(pathToFileURL(resolve(here, 'templates/thumbnail.html')).href);
await p.evaluate(() => document.fonts.ready);
await p.evaluate(s => window.show(s), S);
await p.screenshot({ path: out }); await b.close();
console.log('thumbnail:', out);
