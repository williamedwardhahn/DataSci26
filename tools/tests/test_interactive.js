// Checks on the interactive labs: JavaScript parses, every DOM hook a script asks
// for exists in the markup, and each page is self-contained apart from web fonts.
const fs = require('fs'), path = require('path'), vm = require('vm');

const dir = path.join(__dirname, '..', '..', 'interactive');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();

// The one external origin the labs are allowed to touch. Everything else must be
// bundled, so a lab still works offline and cannot rot when a host goes away.
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com'];

let fails = 0;
const problem = (f, msg) => { console.log(`     ${f}: ${msg}`); fails++; };

for (const f of files) {
  const html = fs.readFileSync(path.join(dir, f), 'utf8');
  const notes = [];

  // 1. every inline script parses
  const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
  let jsLines = 0;
  blocks.forEach((code, i) => {
    jsLines += code.split('\n').length;
    try { new vm.Script(code, { filename: `${f}#${i}` }); }
    catch (e) { notes.push(`script[${i}] ${e.message}`); }
  });

  // 2. every id / radio group a script reaches for exists in the markup
  const js = blocks.join('\n');
  const want = new Set();
  for (const re of [/getElementById\(['"]([\w-]+)['"]\)/g,
                    /\$+\(['"]#([\w-]+)/g,
                    /querySelector\(['"]#([\w-]+)/g]) {
    let m; while ((m = re.exec(js))) want.add(m[1]);
  }
  const have = new Set([...html.matchAll(/\bid="([\w-]+)"/g)].map(m => m[1]));
  const missing = [...want].filter(i => !have.has(i));
  if (missing.length) notes.push(`script needs missing id(s): ${missing.join(', ')}`);

  const groups = new Set([...js.matchAll(/name=\\?['"]([\w-]+)\\?['"]/g)].map(m => m[1]));
  const haveG = new Set([...html.matchAll(/name="([\w-]+)"/g)].map(m => m[1]));
  const missG = [...groups].filter(g => !haveG.has(g) && g !== 'viewport');
  if (missG.length) notes.push(`script needs missing radio group(s): ${missG.join(', ')}`);

  // 3. self-contained apart from fonts
  const ext = [...html.matchAll(/(?:src|href)\s*=\s*["'](https?:\/\/[^"']+)["']/gi)].map(m => m[1]);
  const stray = ext.filter(u => !FONT_HOSTS.some(h => u.includes(h)));
  if (stray.length) notes.push(`external dependency: ${stray[0]}`);

  // 4. house style: shared system, a title, a viewport, a theme control
  if (!/<title>[^<]+<\/title>/i.test(html)) notes.push('no <title>');
  if (!/<meta[^>]+viewport/i.test(html)) notes.push('no viewport meta');
  if (!/href="lab\.css"/.test(html)) notes.push('does not use the shared lab.css');
  if (!/src="lab\.js"/.test(html)) notes.push('does not load lab.js');
  if (!/theme-switch|Lab\.head\(/.test(html)) notes.push('no theme control');
  if (/#0b0d12|#7aa2ff|#121621/.test(html)) notes.push('leftover hard-coded palette from the old design');

  const title = (html.match(/<title>([^<]+)<\/title>/i) || [, '?'])[1];
  const bad = notes.length;
  console.log(`  ${bad ? 'FAIL' : 'ok  '} ${f.padEnd(32)} ${String(blocks.length).padStart(2)} script(s), ` +
              `${String(jsLines).padStart(4)} js lines  ${title.slice(0, 34)}`);
  notes.forEach(n => problem(f, n));
}

// 5. the bundled sample images the shared loader points at must exist
const imgDir = path.join(dir, 'img');
const labjs = fs.readFileSync(path.join(dir, 'lab.js'), 'utf8');
for (const m of labjs.matchAll(/src:\s*'(img\/[\w.-]+)'/g)) {
  if (!fs.existsSync(path.join(dir, m[1]))) problem('lab.js', `sample image missing: ${m[1]}`);
}
const nImg = fs.existsSync(imgDir) ? fs.readdirSync(imgDir).filter(f => /\.(jpg|png)$/.test(f)).length : 0;

console.log(`\n${files.length} interactive labs, ${nImg} bundled images, ${fails} failure(s)`);
process.exit(fails ? 1 : 0);
