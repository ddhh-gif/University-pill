import asyncio, os, sys
import edge_tts

VOICE = sys.argv[2] if len(sys.argv) > 2 else "zh-CN-XiaoyiNeural"
SRC = sys.argv[1]
OUTDIR = SRC.rsplit(".", 1)[0] + "_parts"
os.makedirs(OUTDIR, exist_ok=True)

lines = [l.strip() for l in open(SRC, encoding="utf-8") if l.strip()]
chunks, cur = [], ""
for l in lines:
    if len(cur) + len(l) > 900 and cur:
        chunks.append(cur)
        cur = l
    else:
        cur = cur + "。" + l if cur and not cur.endswith(("。", "！", "？", "：", "；")) else cur + l
if cur:
    chunks.append(cur)


async def one(i, text):
    p = os.path.join(OUTDIR, "%04d.mp3" % i)
    if os.path.exists(p) and os.path.getsize(p) > 1000:
        return
    for attempt in range(5):
        try:
            await edge_tts.Communicate(text, VOICE, rate="+4%").save(p)
            return
        except Exception as e:
            await asyncio.sleep(1 + attempt * 2)
    raise RuntimeError("fail chunk %d" % i)


async def main():
    sem = asyncio.Semaphore(3)

    async def run(i, t):
        async with sem:
            await one(i, t)

    await asyncio.gather(*(run(i, c) for i, c in enumerate(chunks)))
    with open(os.path.join(OUTDIR, "list.txt"), "w") as f:
        for i in range(len(chunks)):
            f.write("file '%04d.mp3'\n" % i)
    print("chunks", len(chunks), "chars", sum(len(c) for c in chunks))


asyncio.run(main())
