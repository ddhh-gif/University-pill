import re, sys

CN = "零一二三四五六七八九十"
def cn(n):
    return CN[n] if n <= 10 else str(n)
pages = open("b.txt", encoding="utf-8").read().split("\f")

lines = []
for i, p in enumerate(pages):
    if i == 0 or "目录" in p:
        continue
    for ln in p.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if re.fullmatch(r"\d+", s):
            continue
        if ". . ." in s or "...." in s:
            continue
        s = re.sub(r"第[一二三四五六七八九十]章\s*马克思主义基本原理期末\s*重点大题汇总\s*\d*", "", s)
        s = re.sub(r"第[一二三四五六七八九十]章\s*马克思主义基本原理期末$", "", s)
        s = re.sub(r"^重点大题汇总\s*\d\.\d\s*重点大题。?$", "", s)
        s = s.strip()
        if not s:
            continue
        lines.append(s)

HEAD = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s+(.*)$")
TOP = re.compile(r"^(\d{1,2})\.\s*")
SUB = re.compile(r"^\(([a-z])\)\s+")
ROM = re.compile(r"^([ivx]+)\.\s+")

paras = []
cur = None
qno = 0
for s in lines:
    if re.match(r"^重点大题汇总", s) or re.match(r"^\d\.\d\s*重点大题", s):
        continue
    if re.match(r"^\d\.\d\s+", s) and not re.match(r"^\d+\.\d+\.\d+", s):
        if cur:
            paras.append(cur)
        cur = "第二部分，经典论断与对应原理"
        continue
    m = HEAD.match(s)
    if m:
        if cur:
            paras.append(cur)
        qno += 1
        cur = "第%d题，%s" % (qno, m.group(4))
        continue
    m = TOP.match(s)
    if m:
        if cur:
            paras.append(cur)
        cur = "第%s，" % cn(int(m.group(1))) + s[m.end():]
        continue
    m = SUB.match(s)
    if m:
        if cur:
            paras.append(cur)
        cur = "其%s，" % CN[ord(m.group(1)) - 96] + s[m.end():]
        continue
    m = ROM.match(s)
    if m:
        if cur:
            paras.append(cur)
        cur = "其%s，" % CN["i ii iii iv v vi".split().index(m.group(1)) + 1] + s[m.end():]
        continue
    cur = (cur or "") + s
if cur:
    paras.append(cur)

def fix(s):
    s = re.sub(r"\s+", "", s)
    s = s.replace(",", "，").replace(";", "；").replace(":", "：")
    s = re.sub(r"\.$", "。", s)
    s = re.sub(r"\.(?=[^0-9])", "。", s)
    s = re.sub(r"。+", "。", s)
    if not s.endswith(("。", "！", "？", "：", "；", "，")):
        s += "。"
    return s

out = ["马原期末重点大题汇总。作者，实空。"]
for p in paras:
    t = fix(p)
    if len(t) < 6:
        continue
    out.append(t)
print("\n".join(out))
