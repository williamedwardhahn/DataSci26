// Parse-check the JavaScript inside each interactive lab, and sanity-check structure.
const fs = require('fs'), path = require('path'), vm = require('vm');
const dir = path.join(__dirname, '..', '..', 'interactive');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();
let fails = 0;

for (const f of files) {
  const html = fs.readFileSync(path.join(dir, f), 'utf8');
  const notes = [];

  // every <script> block must parse as JavaScript
  const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
  let jsLines = 0;
  blocks.forEach((code, i) => {
    jsLines += code.split('\n').length;
    try { new vm.Script(code, { filename: `${f}#script${i}` }); }
    catch (e) { notes.push(`script[${i}] ${e.message}`); fails++; }
  });

  // structural expectations for a self-contained teaching page
  if (!/<title>[^<]+<\/title>/i.test(html)) { notes.push('no <title>'); fails++; }
  if (!/<meta[^>]+viewport/i.test(html)) notes.push('warn: no viewport meta (mobile)');
  const ext = [...html.matchAll(/(?:src|href)\s*=\s*["'](https?:\/\/[^"']+)["']/gi)].map(m => m[1]);
  const extAssets = ext.filter(u => /\.(js|css|woff2?|ttf)(\?|$)/i.test(u));
  if (extAssets.length) { notes.push(`external asset dep: ${extAssets[0]}`); fails++; }

  const title = (html.match(/<title>([^<]+)<\/title>/i) || [, '?'])[1];
  const status = notes.filter(n => !n.startsWith('warn:')).length ? 'FAIL' : 'ok  ';
  console.log(`${status} ${f.padEnd(34)} ${String(blocks.length).padStart(2)} script(s), ${String(jsLines).padStart(4)} js lines  ${title.slice(0, 40)}`);
  notes.forEach(n => console.log(`       ${n}`));
}
console.log(`\n${files.length} interactive labs, ${fails} failure(s)`);
process.exit(fails ? 1 : 0);
