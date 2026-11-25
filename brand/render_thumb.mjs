import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + process.cwd() + '/thumb.html'); await p.evaluate(() => document.fonts.ready);
for (const k of ['A','B']) { await p.evaluate(k => window.show(k), k); await p.screenshot({ path: `thumb01_${k}.png` }); }
await b.close();
