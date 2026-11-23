#!/usr/bin/env python3
"""Rebuild Untitled-1.pdf from the images referenced in Untitled-1.md.

- One image per A4 page, scaled-to-fit (no cropping, no splitting).
- Images are read in the order they appear in the markdown.
- Also fixes the markdown references to be self-contained: copies the
  images into images/ with sequential names and rewrites the .md.
"""
import os
import re
import shutil

from PIL import Image, ImageOps

MD = "/home/zihan/Desktop/电工实验/Untitled-1.md"
OUT_PDF = "/home/zihan/Desktop/电工实验/Untitled-1.pdf"
IMG_DIR = "/home/zihan/Desktop/电工实验/images"

# A4 at 300 dpi
A4_W, A4_H = 2480, 3508
RES = 300
QUALITY = 95


def extract_image_paths(md_path):
    paths = []
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*!\[[^\]]*\]\(([^)\s]+)", line)
            if m:
                paths.append(m.group(1))
    return paths


def fit_into(img, page_w, page_h):
    img = img.convert("RGB")
    w, h = img.size
    scale = min(page_w / w, page_h / h)
    nw = max(1, round(w * scale))
    nh = max(1, round(h * scale))
    return img.resize((nw, nh), Image.LANCZOS)


def main():
    paths = extract_image_paths(MD)
    if not paths:
        raise SystemExit("no image references found in markdown")

    os.makedirs(IMG_DIR, exist_ok=True)

    pages = []
    new_lines = []
    for i, p in enumerate(paths, 1):
        if not os.path.exists(p):
            raise SystemExit(f"missing image: {p}")

        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im)
            fitted = fit_into(im, A4_W, A4_H)

        canvas = Image.new("RGB", (A4_W, A4_H), "white")
        x = (A4_W - fitted.width) // 2
        y = (A4_H - fitted.height) // 2
        canvas.paste(fitted, (x, y))
        pages.append(canvas)

        # self-contained copy + relative markdown reference
        rel_name = f"{i:02d}.jpg"
        shutil.copyfile(p, os.path.join(IMG_DIR, rel_name))
        new_lines.append(f"![]({os.path.join('images', rel_name)})")

    pages[0].save(
        OUT_PDF, "PDF", save_all=True, append_images=pages[1:],
        resolution=RES, quality=QUALITY,
    )

    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n\n".join(new_lines) + "\n")

    print(f"Wrote {OUT_PDF}: {len(pages)} pages")
    print(f"Rewrote {MD} with {len(new_lines)} relative references")


if __name__ == "__main__":
    main()
