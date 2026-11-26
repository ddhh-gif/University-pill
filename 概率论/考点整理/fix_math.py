#!/usr/bin/env python3
"""修复被转换器破坏的 Markdown 数学公式（幂等，可反复运行）。

修三类问题：
1. 独占一行的 `[` / `]`   -> `$$`（行间公式）
2. 正文里被剥掉定界符的 `(...)` -> `$...$`（行内公式）
3. `,\\Big|,` / `,\\big|,` -> `\\,\\Big|\\,` / `\\,\\big|\\,`
   （原文 `\\,` 被误写成逗号，竖线两侧的空格残留）

用法:
    python3 fix_math.py 文件.md [更多.md ...]
"""
import re
import sys
from pathlib import Path

MATHY = re.compile(r"[\\^_=<>]")
VAR = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z][A-Za-z0-9_]*)*")
APPLY = re.compile(r"[A-Za-z][A-Za-z0-9_]*\([A-Za-z0-9_,\\{}^]*\)")
MATH_ONLY = re.compile(r"[A-Za-z0-9_\\{}^()\s,=<>+\-*/.|:]+")


def is_math(content: str) -> bool:
    content = content.strip()
    if not content:
        return False
    if MATHY.search(content):
        return True
    if VAR.fullmatch(content):
        return True
    if APPLY.fullmatch(content):
        return True
    if MATH_ONLY.fullmatch(content) and any(c.isupper() for c in content):
        return True
    return False


def fix_pipe(line: str) -> str:
    return line.replace(r",\Big|,", r"\,\Big|\,", ).replace(
        r",\big|,", r"\,\big|\,")


def fix_inline(line: str) -> str:
    """把行内 `(公式)` 包成 `$公式$`；跳过代码、已有 $...$ 和普通括号。"""
    out = []
    i, n = 0, len(line)
    in_code = in_dollar = False
    while i < n:
        ch = line[i]
        if ch == "`":
            in_code = not in_code
            out.append(ch)
            i += 1
            continue
        if ch == "$" and not in_code:
            in_dollar = not in_dollar
            out.append(ch)
            i += 1
            continue
        if ch == "(" and not in_code and not in_dollar:
            depth, j, closed = 0, i, False
            while j < n:
                if line[j] == "(":
                    depth += 1
                elif line[j] == ")":
                    depth -= 1
                    if depth == 0:
                        closed = True
                        break
                j += 1
            if closed:
                content = line[i + 1:j]
                if "$" not in content and is_math(content):
                    out.append("$" + content + "$")
                    i = j + 1
                    continue
        out.append(ch)
        i += 1
    return "".join(out)


def fix_text(text: str) -> str:
    out = []
    in_display = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == "[":
            out.append("$$")
            in_display = True
            continue
        if stripped == "]":
            out.append("$$")
            in_display = False
            continue
        if stripped == "$$":
            out.append(line)
            in_display = not in_display
            continue
        if in_display:
            out.append(fix_pipe(line))
        else:
            out.append(fix_inline(fix_pipe(line)))
    return "\n".join(out)


def main(paths):
    for p in map(Path, paths):
        src = p.read_text(encoding="utf-8")
        fixed = fix_text(src)
        if fixed == src:
            print(f"未改动: {p}")
        else:
            p.write_text(fixed, encoding="utf-8")
            print(f"已修复: {p}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
