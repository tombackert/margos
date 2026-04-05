#!/usr/bin/env python3
import sys, re

def format_table(lines):
    rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines]
    n = max(len(r) for r in rows)
    for r in rows:
        while len(r) < n:
            r.append('')
    widths = [max(len(r[i]) for r in rows) for i in range(n)]
    out = []
    for row in rows:
        is_sep = all(re.match(r'^:?-+:?$', c) or c == '' for c in row)
        cells = [('-' * widths[i]) if is_sep else row[i].ljust(widths[i]) for i in range(n)]
        out.append('| ' + ' | '.join(cells) + ' |')
    return out

def main():
    path = sys.argv[1]
    with open(path) as f:
        lines = f.readlines()
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith('|'):
            block = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                block.append(lines[i].rstrip('\n'))
                i += 1
            out.extend(l + '\n' for l in format_table(block))
        else:
            out.append(lines[i])
            i += 1
    with open(path, 'w') as f:
        f.writelines(out)

if __name__ == '__main__':
    main()
