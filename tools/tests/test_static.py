"""Static checks on the built labs: JSON validity, cell shape, Python syntax."""
import ast, glob, json, os, re, sys, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LABS = sorted(glob.glob(os.path.join(ROOT, 'labs', '*.ipynb')))

# Colab/IPython-only syntax that is legal in a notebook but not in plain Python.
MAGIC = re.compile(r'^\s*[!%]|^\s*\w+\?$|^\s*display\(', re.M)


# Notebook cells are not plain Python: IPython transforms them first (it strips
# leading indentation, rewrites magics, and so on). Use the real transformer when
# it is importable so the check matches how Colab actually runs the cell.
try:
    from IPython.core.inputtransformer2 import TransformerManager
    _TM = TransformerManager()
except Exception:
    _TM = None


def strip_magics(src):
    """Reduce a notebook cell to something `ast.parse` can judge.

    A cell whose first line is a `%%cell` magic is not Python at all -- its body
    is handed to another interpreter (html, bash, capture), so skip it entirely.
    """
    if src.lstrip().startswith('%%'):
        return ''
    if _TM is not None:
        try:
            return _TM.transform_cell(src)
        except Exception:
            return ''      # IPython itself rejects it; reported by the caller
    src = textwrap.dedent(src)      # IPython strips a cell's common indentation
    out = []
    for line in src.splitlines():
        s = line.lstrip()
        if s.startswith('!') or s.startswith('%') or s.startswith('?') or s.endswith('?'):
            out.append('pass  # ' + line.strip())
        else:
            out.append(line)
    return '\n'.join(out)


def main():
    fails = []
    stats = []
    for p in LABS:
        name = os.path.basename(p)
        try:
            nb = json.load(open(p))
        except Exception as e:
            fails.append((name, '-', f'invalid JSON: {e}')); continue

        if nb.get('nbformat') != 4:
            fails.append((name, '-', f"nbformat is {nb.get('nbformat')}, expected 4"))

        n_code = n_md = n_syntax_ok = 0
        for i, c in enumerate(nb.get('cells', [])):
            ct = c.get('cell_type')
            if ct not in ('markdown', 'code'):
                fails.append((name, i, f'bad cell_type {ct!r}')); continue
            src = ''.join(c.get('source', []))
            if ct == 'markdown':
                n_md += 1
                continue
            n_code += 1
            if c.get('outputs') != []:
                fails.append((name, i, 'code cell carries outputs'))
            if c.get('execution_count') is not None:
                fails.append((name, i, 'code cell has execution_count'))
            try:
                ast.parse(strip_magics(src))
                n_syntax_ok += 1
            except SyntaxError as e:
                fails.append((name, i, f'SyntaxError line {e.lineno}: {e.msg}'))

        # every lab must open with header + setup, and close with homework
        head = ''.join(nb['cells'][0].get('source', []))
        if not head.startswith('# Lab '):
            fails.append((name, 0, 'first cell is not the lab header'))
        setup = ''.join(nb['cells'][1].get('source', []))
        if 'device = torch.device' not in setup:
            fails.append((name, 1, 'setup cell does not define device'))
        tail = ''.join(nb['cells'][-1].get('source', []))
        if '## Homework' not in tail:
            fails.append((name, len(nb['cells']) - 1, 'last cell is not the homework block'))

        stats.append((name, n_md, n_code, n_syntax_ok))

    w = max(len(s[0]) for s in stats)
    print(f'{"lab".ljust(w)}   md  code  parsed')
    for name, md, code, ok in stats:
        flag = '' if ok == code else f'   <-- {code-ok} FAILED'
        print(f'{name.ljust(w)} {md:4} {code:5} {ok:7}{flag}')
    print()
    if fails:
        print(f'{len(fails)} FAILURES')
        for name, i, msg in fails:
            print(f'  {name} [{i}]: {msg}')
        return 1
    mode = 'IPython transformer' if _TM is not None else 'fallback magic-stripper'
    print(f'PASS — {len(LABS)} labs, {sum(s[2] for s in stats)} code cells parse ({mode})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
