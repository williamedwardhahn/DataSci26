"""Split notebooks into heading-delimited sections; used to compose course labs."""
import json, os, re, glob

def sections(path):
    """Yield (level, title, start, end) for each markdown heading in a notebook."""
    nb = json.load(open(path))
    cells = nb.get('cells', [])
    marks = []
    for i, c in enumerate(cells):
        if c.get('cell_type') != 'markdown':
            continue
        txt = ''.join(c.get('source', []))
        m = re.match(r'^\s*(#{1,4})\s*(.+)', txt)
        if m:
            marks.append((i, len(m.group(1)), m.group(2).strip().splitlines()[0][:60]))
    out = []
    for n, (i, lvl, title) in enumerate(marks):
        end = len(cells)
        for j, l2, _ in marks[n + 1:]:
            if l2 <= lvl:
                end = j
                break
        out.append((lvl, title, i, end))
    return out

def load(path):
    return json.load(open(path))['cells']

if __name__ == '__main__':
    root = os.path.join(os.path.dirname(__file__), '..', '_source', 'notebooks')
    for p in sorted(glob.glob(os.path.join(root, '**', '*.ipynb'), recursive=True)):
        rel = os.path.relpath(p, root)
        for lvl, title, a, b in sections(p):
            print(f'{rel}\t{lvl}\t{a}\t{b}\t{b-a}\t{title}')
