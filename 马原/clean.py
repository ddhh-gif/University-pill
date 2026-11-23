import re, sys

WM = set("帮数高")
CN = "零一二三四五六七八九十"


def cn_num(n):
    return CN[n] if n < 11 else str(n)


def strip_wm(line):
    line = line.replace("课程讲解更清晰，仅 2 小时", "")
    line = line.replace("课程讲解更清晰, 仅 2 小时", "")
    toks = line.split()
    toks = [t for t in toks if not all(c in WM for c in t)]
    return "".join(toks)


def is_wm_only(line):
    s = line.strip()
    return s == "" or all(c in WM or c.isspace() for c in s)


COVER = ("适用所有期末考", "2020 年 12 月最新版", "2020年12月最新版")
HEAD = re.compile(
    r"^(第[一二三四五六七八九十]+[章节]|"
    r"[一二三四五六七八九十]+、|"
    r"（[一二三四五六七八九十]+）|"
    r"\(\d+\)|（\d+[\)）]|"
    r"老师[:：])"
)
NUM = re.compile(r"^(\d{1,2})[\.、]\s*(?=\D)")

txt = open(sys.argv[1], encoding="utf-8").read().split("\n")
raw_lines = []
for raw in txt:
    s = strip_wm(raw).strip()
    if not s:
        continue
    if "课程讲解更清晰" in raw:
        continue
    if is_wm_only(raw):
        continue
    if any(c in s for c in COVER):
        continue
    raw_lines.append(s)

paras = []
for s in raw_lines:
    num = NUM.match(s)
    if num:
        s = "第%s，" % cn_num(int(num.group(1))) + s[num.end():]
        paras.append(s)
        continue
    if HEAD.match(s) or s.startswith("第") and len(s) < 40:
        paras.append(s)
    elif not paras:
        paras.append(s)
    else:
        paras[-1] = paras[-1] + s

out = [p.replace("考案", "考察") for p in paras if len(p) > 1]
print("\n".join(out))
