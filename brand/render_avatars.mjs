import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
await p.goto('file://' + process.cwd() + '/avatars.html'); await p.evaluate(() => document.fonts.ready);
for (const k of ['A','B','C','D']) { await p.evaluate(k => window.show(k), k); await p.screenshot({ path: `avatar_${k}.png` }); }
await b.close();
