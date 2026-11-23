#!/usr/bin/env python3
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
PLACEHOLDER = "\x00{}\x00"


def fix(text: str) -> tuple[str, int]:
    protected: list[str] = []

    def protect(match: re.Match) -> str:
        protected.append(match.group(0))
        return PLACEHOLDER.format(len(protected) - 1)

    lines = text.splitlines(keepends=True)
    out, in_fence, fence_mark = [], False, ""
    for line in lines:
        m = FENCE.match(line)
        if m:
            mark = m.group(1)
            if not in_fence:
                in_fence, fence_mark = True, mark
            elif mark == fence_mark:
                in_fence = False
            out.append(line)
        elif in_fence:
            out.append(line)
        else:
            out.append(INLINE_CODE.sub(protect, line))
    text = "".join(out)

    def display_block(m: re.Match) -> str:
        indent, body = m.group(1), m.group(2)
        lines = [indent + line.strip() for line in body.strip().splitlines()]
        return indent + "$$\n" + "\n".join(lines) + "\n" + indent + "$$"

    text, n_block = re.subn(
        r"(?m)^([ \t]*)\\\[[ \t]*\r?\n(.*?)\r?\n[ \t]*\\\][ \t]*$",
        display_block,
        text,
        flags=re.S,
    )
    text, n_display = re.subn(
        r"(?<!\\)\\\[(.*?)(?<!\\)\\\]",
        lambda m: "$$" + m.group(1).strip() + "$$",
        text,
        flags=re.S,
    )
    text, n_inline = re.subn(
        r"(?<!\\)\\\((.*?)(?<!\\)\\\)",
        lambda m: "$" + m.group(1) + "$",
        text,
    )

    text = re.sub(
        r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], text
    )
    return text, n_block + n_display + n_inline


def main(paths: list[str]) -> None:
    for p in paths:
        path = Path(p)
        original = path.read_text(encoding="utf-8")
        fixed, count = fix(original)
        if count:
            path.write_text(fixed, encoding="utf-8")
        print(f"{path}: {count} 处")
        if count == 0 and r"\(" in original:
            print("  警告：仍有未处理的 \\(，请人工检查", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法: python3 fix_latex.py 文件1.md [文件2.md ...]")
    main(sys.argv[1:])
