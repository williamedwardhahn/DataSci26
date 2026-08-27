"""Check every external URL referenced by the course (labs, docs, interactive)."""
import concurrent.futures as cf, glob, json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URL = re.compile(r'https?://[^\s"\'<>)\]\\`]+')

# Hosts that refuse non-browser clients. A 403 from these says nothing about
# whether the link works for a student, so report them separately.
BOT_BLOCKED = ('chatgpt.com', 'claude.ai', 'i.stack.imgur.com', 'openai.com')

def skip(u):
    """Placeholders and bare URL prefixes built up in code are not real links."""
    return ('YOUR-USERNAME' in u
            or u.endswith('/d/')
            or u.rstrip('/').endswith(('/presentation', '/spreadsheets')))
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/120 Safari/537.36'}


def harvest():
    found = {}
    for p in glob.glob(os.path.join(ROOT, 'labs', '*.ipynb')):
        for c in json.load(open(p))['cells']:
            for u in URL.findall(''.join(c['source'])):
                found.setdefault(u.rstrip('.,;:'), set()).add(os.path.basename(p))
    for p in ['README.md', 'project/README.md', 'setup/README.md'] + \
             [os.path.relpath(x, ROOT) for x in glob.glob(os.path.join(ROOT, 'interactive', '*.html'))]:
        f = os.path.join(ROOT, p)
        if not os.path.exists(f):
            continue
        for u in URL.findall(open(f, errors='ignore').read()):
            found.setdefault(u.rstrip('.,;:'), set()).add(p)
    return found


def check(u):
    for attempt in range(3):
        for method in ('HEAD', 'GET'):
            try:
                r = urllib.request.Request(u, method=method, headers=UA)
                with urllib.request.urlopen(r, timeout=25) as resp:
                    return u, resp.status, ''
            except urllib.error.HTTPError as e:
                if e.code == 429:          # rate limited -- back off and retry
                    time.sleep(2 + 3 * attempt)
                    break
                if e.code in (403, 405) and method == 'HEAD':
                    continue
                return u, e.code, e.reason
            except Exception as e:
                if method == 'HEAD':
                    continue
                if attempt < 2:
                    time.sleep(1 + attempt)
                    break
                return u, 0, type(e).__name__
    return u, 429, 'rate limited after retries'


def _unused(u):
    for method in ('HEAD', 'GET'):
        try:
            r = urllib.request.Request(u, method=method, headers=UA)
            with urllib.request.urlopen(r, timeout=20) as resp:
                return u, resp.status, ''
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 429) and method == 'HEAD':
                continue
            return u, e.code, e.reason
        except Exception as e:
            if method == 'HEAD':
                continue
            return u, 0, type(e).__name__
    return u, 0, 'unreachable'


def main():
    found = harvest()
    urls = sorted(u for u in found if not skip(u))
    skipped = sorted(u for u in found if skip(u))
    print(f'checking {len(urls)} unique URLs...\n')
    results = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for u, code, msg in ex.map(check, urls):
            results.append((u, code, msg))
    ok = [r for r in results if 200 <= r[1] < 400]
    rest = [r for r in results if not (200 <= r[1] < 400)]
    blocked = [r for r in rest if any(h in r[0] for h in BOT_BLOCKED)]
    bad = [r for r in rest if r not in blocked]
    for u, code, msg in sorted(bad, key=lambda r: -r[1]):
        where = ', '.join(sorted(found[u]))
        print(f'  {code or "ERR":>4}  {u}')
        print(f'        in: {where}' + (f'  ({msg})' if msg else ''))
    if blocked:
        print('  bot-blocked (works in a browser, cannot verify from a script):')
        for u, code, _ in sorted(blocked):
            print(f'    {code}  {u}')
    if skipped:
        print(f'  skipped {len(skipped)} placeholder/prefix strings')
    print(f'\n{len(ok)} reachable, {len(blocked)} unverifiable, {len(bad)} broken, {len(urls)} checked')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
