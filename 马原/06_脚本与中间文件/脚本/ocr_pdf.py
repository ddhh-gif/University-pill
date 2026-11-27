#!/usr/bin/env python3
"""逐页 OCR（RapidOCR），支持断点续跑与完整性检查。"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pymupdf
from rapidocr_onnxruntime import RapidOCR


def render(page, zoom):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 3:
        arr = arr[:, :, ::-1]  # RGB -> BGR
    return np.ascontiguousarray(arr)


def parse_result(res):
    items = []
    if not res:
        return items
    for box, text, score in res:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        items.append(
            {
                "text": text,
                "score": round(float(score), 4),
                "x0": round(min(xs), 1),
                "y0": round(min(ys), 1),
                "x1": round(max(xs), 1),
                "y1": round(max(ys), 1),
            }
        )
    items.sort(key=lambda it: (it["y0"], it["x0"]))
    return items


def ocr_banded(engine, img, band=900):
    """重叠分带 OCR，避免整页缩放导致长行漏检。"""
    H = img.shape[0]
    step = band // 2
    items = []
    y = 0
    while True:
        y2 = min(H, y + band)
        res, _ = engine(img[y:y2])
        for box, text, score in res or []:
            ys = [p[1] + y for p in box]
            xs = [p[0] for p in box]
            y0, y1 = min(ys), max(ys)
            x0, x1 = min(xs), max(xs)
            # 贴带边的框丢弃，交给相邻带完整识别
            if (y > 0 and y0 < y + 6) or (y2 < H and y1 > y2 - 6):
                continue
            items.append(
                {
                    "text": text,
                    "score": round(float(score), 4),
                    "x0": round(x0, 1),
                    "y0": round(y0, 1),
                    "x1": round(x1, 1),
                    "y1": round(y1, 1),
                }
            )
        if y2 >= H:
            break
        y += step

    items.sort(key=lambda it: (it["y0"], it["x0"]))
    out = []
    for it in items:
        dup = False
        for prev in out[-4:]:
            if (
                abs(prev["y0"] - it["y0"]) < 12
                and abs(prev["x0"] - it["x0"]) < 12
                and prev["text"] == it["text"]
            ):
                dup = True
                break
        if not dup:
            out.append(it)
    return out


def build_lines(items):
    """按垂直重叠把文字框合并成行，行内按 x 排序。"""
    lines = []
    for it in sorted(items, key=lambda x: (x["y0"], x["x0"])):
        h = it["y1"] - it["y0"]
        placed = False
        for ln in reversed(lines[-3:]):
            lh = ln["y1"] - ln["y0"]
            overlap = min(ln["y1"], it["y1"]) - max(ln["y0"], it["y0"])
            if overlap > 0.5 * min(h, lh):
                ln["items"].append(it)
                ln["y0"] = min(ln["y0"], it["y0"])
                ln["y1"] = max(ln["y1"], it["y1"])
                placed = True
                break
        if not placed:
            lines.append({"y0": it["y0"], "y1": it["y1"], "items": [it]})

    out = []
    for ln in sorted(lines, key=lambda l: (l["y0"] + l["y1"]) / 2):
        parts = sorted(ln["items"], key=lambda it: it["x0"])
        text = ""
        prev = None
        for it in parts:
            if prev is not None and it["x0"] - prev["x1"] > 8:
                text += " "
            text += it["text"]
            prev = it
        out.append(text)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("--zoom", type=float, default=2.0)
    ap.add_argument("--pages", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    engine = RapidOCR()
    doc = pymupdf.open(args.pdf)
    total = doc.page_count

    if args.pages:
        wanted = set()
        for part in args.pages.split(","):
            if "-" in part:
                a, b = part.split("-")
                wanted.update(range(int(a), int(b) + 1))
            else:
                wanted.add(int(part))
        page_nos = sorted(p for p in wanted if 1 <= p <= total)
    else:
        page_nos = list(range(1, total + 1))

    print(f"PDF: {args.pdf}")
    print(f"pages: {total}, zoom: {args.zoom}")
    for pno in page_nos:
        txt_path = os.path.join(args.outdir, f"page_{pno:02d}.txt")
        js_path = os.path.join(args.outdir, f"page_{pno:02d}.json")
        if not args.force and os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            print(f"page {pno:2d}: skip (exists)")
            continue
        t0 = time.time()
        img = render(doc[pno - 1], args.zoom)
        items = ocr_banded(engine, img)
        text = "\n".join(build_lines(items))
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text + ("\n" if text else ""))
        with open(js_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=1)
        avg = sum(it["score"] for it in items) / len(items) if items else 0
        print(
            f"page {pno:2d}: {len(items):3d} lines, {len(text):5d} chars, "
            f"avg {avg:.3f}, {time.time() - t0:.1f}s"
        )

    # 合并 + 完整性检查
    merged = []
    empty = []
    for pno in range(1, total + 1):
        txt_path = os.path.join(args.outdir, f"page_{pno:02d}.txt")
        if not os.path.exists(txt_path):
            empty.append(pno)
            merged.append("")
            continue
        text = open(txt_path, encoding="utf-8").read().strip()
        if not text:
            empty.append(pno)
        merged.append(text)
    out = os.path.join(args.outdir, "_merged.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\f".join(merged) + "\n")
    print(f"merged: {out}  total chars: {sum(len(x) for x in merged)}")
    if empty:
        print(f"WARNING empty/missing pages: {empty}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
