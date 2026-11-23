#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""热学_整理版.md -> 热学_整理版.tex (dense layout, XeLaTeX + xeCJK)."""
import re

SRC = '/home/zihan/Desktop/考试资料/热学_整理版.md'
OUT = '/home/zihan/Desktop/考试资料/热学_整理版.tex'

raw = open(SRC, encoding='utf-8').read()

# ---- global fixes (specific to this document) ----
raw = raw.replace('$R=k*N_A$', '\\(R=k N_A\\)')   # $...$ + `*`
raw = re.sub(r'\\R(?![A-Za-z])', 'R', raw)           # stray \R (not \Rightarrow etc.)
raw = raw.replace('\\rm 产生', '\\text{产生}')        # \rm with CJK -> \text

def inline(text):
    """Inline markdown -> LaTeX, leaving \(...\) math untouched."""
    parts = re.split(r'(\\\(.*?\\\))', text)
    out = []
    for p in parts:
        if p.startswith('\\(') and p.endswith('\\)'):
            out.append(p)                      # math verbatim
        else:
            p = p.replace('→', '\\(\\rightarrow\\)')
            p = p.replace('>', '\\(>\\)')
            p = p.replace('<', '\\(<\\)')
            p = p.replace('≠', '\\(\\ne\\)')
            p = p.replace('×', '\\(\\times\\)')
            p = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', p)
            p = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', p)   # link -> anchor text
            out.append(p)
    return ''.join(out)

def split_cells(line):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]

def is_sep_line(line):
    if '|' not in line:
        return False
    cells = split_cells(line)
    if not cells:
        return False
    return all(re.fullmatch(r':?-{3,}:?', c.replace(' ', '')) for c in cells)

def colspec(ncol):
    return 'l' if ncol == 1 else 'l' + 'Y' * (ncol - 1)

lines = raw.split('\n')
body = []
i, n = 0, len(lines)

while i < n:
    line = lines[i]
    s = line.strip()

    if s == '':
        i += 1
        continue

    # headings
    m = re.match(r'^(#{1,3})\s+(.*)$', line)
    if m:
        lvl, txt = len(m.group(1)), inline(m.group(2).strip())
        if txt == '热学（整理版）':
            body.append('\\begin{center}\\LARGE\\bfseries 热学（整理版）\\end{center}')
        elif lvl == 1:
            body.append('\\section*{%s}' % txt)
        elif lvl == 2:
            body.append('\\subsection*{%s}' % txt)
        else:
            body.append('\\subsubsection*{%s}' % txt)
        i += 1
        continue

    # table
    if s.startswith('|') and i + 1 < n and is_sep_line(lines[i + 1]):
        header = split_cells(line)
        i += 2
        rows = []
        while i < n and lines[i].strip().startswith('|'):
            rows.append(split_cells(lines[i]))
            i += 1
        ncol = len(header)
        body.append('\\begin{center}\\small')
        body.append('\\begin{tabularx}{\\linewidth}{%s}' % colspec(ncol))
        body.append('\\toprule')
        body.append(' & '.join('\\textbf{%s}' % inline(c) for c in header) + ' \\\\')
        body.append('\\midrule')
        for r in rows:
            r = (r + [''] * ncol)[:ncol]
            body.append(' & '.join(inline(c) for c in r) + ' \\\\')
        body.append('\\bottomrule')
        body.append('\\end{tabularx}\\end{center}')
        continue

    # blockquote -> note box
    if s.startswith('>'):
        buf = []
        while i < n and lines[i].strip().startswith('>'):
            buf.append(lines[i].strip()[1:].strip())
            i += 1
        body.append('\\begin{notebox}%s\\end{notebox}' % inline(' '.join(buf)))
        continue

    # unordered list
    if re.match(r'^-\s+', s):
        body.append('\\begin{itemize}')
        while i < n and re.match(r'^-\s+', lines[i].strip()):
            body.append('\\item %s' % inline(lines[i].strip()[1:].strip()))
            i += 1
        body.append('\\end{itemize}')
        continue

    # ordered list
    if re.match(r'^\d+\.\s+', s):
        body.append('\\begin{enumerate}')
        while i < n and re.match(r'^\d+\.\s+', lines[i].strip()):
            body.append('\\item %s' % inline(re.sub(r'^\d+\.\s+', '', lines[i].strip())))
            i += 1
        body.append('\\end{enumerate}')
        continue

    # horizontal rule
    if re.fullmatch(r'-{3,}', s):
        i += 1
        continue

    # display math
    if s.startswith('\\['):
        if '\\]' in s:
            body.append(s)
            i += 1
        else:
            block = [s]
            i += 1
            while i < n and '\\]' not in lines[i]:
                block.append(lines[i])
                i += 1
            if i < n:
                block.append(lines[i])
                i += 1
            body.append('\n'.join(block))
        continue

    # plain paragraph line(s)
    para = [s]
    i += 1
    while i < n and lines[i].strip() != '':
        t = lines[i].strip()
        if (re.match(r'^(#{1,3}\s|-\s|\d+\.\s|>|\|)', t)
                or t.startswith('\\[') or re.fullmatch(r'-{3,}', t)):
            break
        para.append(t)
        i += 1
    body.append(inline(' '.join(para)))

content = '\n\n'.join(body)

preamble = r"""\documentclass[10pt,a4paper]{article}
\usepackage[a4paper,margin=1.3cm,top=1.0cm,bottom=1.0cm,footskip=8pt]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\usepackage[most]{tcolorbox}

\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont[AutoFakeBold=2.5]{Noto Serif CJK SC}
\setCJKsansfont[AutoFakeBold=2.5]{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}

% --- dense layout ---
\setlength{\parindent}{0pt}
\setlength{\parskip}{1.5pt}
\linespread{0.96}
\emergencystretch=2em
\allowdisplaybreaks
\setlength{\abovedisplayskip}{3pt plus 1pt}
\setlength{\belowdisplayskip}{3pt plus 1pt}
\setlength{\abovedisplayshortskip}{1pt}
\setlength{\belowdisplayshortskip}{1pt}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{0.92}
\setlist{nosep,leftmargin=1.5em}

\titleformat{\section}{\large\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{6pt}{1pt}
\titleformat{\subsection}{\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{4pt}{0.5pt}
\titleformat{\subsubsection}{\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\subsubsection}{0pt}{3pt}{0.5pt}

\newcolumntype{Y}{>{\centering\arraybackslash}X}

\newtcolorbox{notebox}{colback=gray!7,colframe=gray!50,boxrule=0.4pt,arc=1mm,
  left=4pt,right=4pt,top=2pt,bottom=2pt,breakable,before skip=3pt,after skip=3pt}

\begin{document}
"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(preamble + content + '\n\n\\end{document}\n')

print('wrote', OUT)
