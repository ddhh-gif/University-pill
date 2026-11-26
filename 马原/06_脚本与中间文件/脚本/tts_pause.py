import asyncio, os, sys, subprocess
import edge_tts

SRC = sys.argv[1]
VOICE = sys.argv[2] if len(sys.argv) > 2 else "zh-CN-XiaoyiNeural"
SHORT = float(sys.argv[3]) if len(sys.argv) > 3 else 0.40   # 普通分行
LONG = float(sys.argv[4]) if len(sys.argv) > 4 else 0.85    # 标题/章节前后
RATE = "+4%"

OUTDIR = SRC.rsplit(".", 1)[0] + "_lines"
FINAL = SRC.rsplit(".", 1)[0] + "_pause.mp3"
os.makedirs(OUTDIR, exist_ok=True)

lines = [l.strip() for l in open(SRC, encoding="utf-8") if l.strip()]


def is_heading(s: str) -> bool:
    return ("【" not in s) and (not s.endswith(("。", "！", "？", "；", "：")))


async def synth(i, text):
    p = os.path.join(OUTDIR, "%04d.mp3" % i)
    if os.path.exists(p) and os.path.getsize(p) > 1000:
        return
    for attempt in range(6):
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(p)
            return
        except Exception:
            await asyncio.sleep(1 + attempt * 2)
    raise RuntimeError("fail line %d" % i)


def make_silence(name, dur):
    p = os.path.join(OUTDIR, name)
    if os.path.exists(p):
        return
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", str(dur), "-c:a", "libmp3lame", "-b:a", "48k", p],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


async def main():
    sem = asyncio.Semaphore(4)

    async def run(i, t):
        async with sem:
            await synth(i, t)

    await asyncio.gather(*(run(i, l) for i, l in enumerate(lines)))
    print("synth done:", len(lines), "lines", flush=True)

    make_silence("_short.mp3", SHORT)
    make_silence("_long.mp3", LONG)

    lst = os.path.join(OUTDIR, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for i, l in enumerate(lines):
            f.write("file '%04d.mp3'\n" % i)
            if i < len(lines) - 1:
                gap = LONG if (is_heading(l) or is_heading(lines[i + 1])) else SHORT
                f.write("file '%s'\n" % ("_long.mp3" if gap == LONG else "_short.mp3"))

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", "-ac", "1", FINAL],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("final:", FINAL, flush=True)


asyncio.run(main())
