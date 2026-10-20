# -*- coding: utf-8 -*-
"""Анализ «висящих» (статичных) участков записи демо-видео.

Дамп кадров 2 fps -> scale 64x36 -> gray -> rawvideo в pipe.
Кадр «статичный», если изменилось < 2% пикселей (|d| > 30).
Серии статики >= 4 c печатаются и сохраняются в idle_blocks.json.

Запуск: python analyze_idle.py [путь_к_видео]
Путь к ffmpeg берётся из imageio-ffmpeg (pip install imageio-ffmpeg):
в билде Playwright (ms-playwright\\ffmpeg-1011) нет rawvideo-муксера.
"""
import json
import os
import subprocess
import sys

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SRC = sys.argv[1] if len(sys.argv) > 1 else "input.webm"
OUT = "idle_blocks.json"

FPS = 2                 # частота анализа кадров
W, H = 64, 36           # размер кадра анализа
FRAME = W * H
TH = 0.02               # порог «статичности»: < 2% изменившихся пикселей
DIFF = 30               # порог отличия одного пикселя
MIN_IDLE_SEC = 4        # минимальная длина статичного блока


def read_exact(stream, n):
    """Пайп возвращает куски произвольной длины — читать строго n байт."""
    buf = b""
    while len(buf) < n:
        chunk = stream.read(n - len(buf))
        if not chunk:
            return buf
        buf += chunk
    return buf


def main():
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-an",
           "-i", SRC,
           "-vf", "fps=%d,scale=%d:%d" % (FPS, W, H),
           "-pix_fmt", "gray", "-f", "rawvideo", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    fracs = []
    prev = None
    while True:
        buf = read_exact(proc.stdout, FRAME)
        if len(buf) < FRAME:
            break
        if prev is None:
            fracs.append(1.0)
        else:
            changed = sum(1 for a, b in zip(prev, buf) if abs(a - b) > DIFF)
            fracs.append(changed / float(FRAME))
        prev = buf
    proc.wait()

    total = len(fracs) / float(FPS)
    print("duration~%.1fs frames=%d" % (total, len(fracs)))

    idle = [f < TH for f in fracs]
    blocks = []
    i, n = 0, len(idle)
    while i < n:
        if idle[i]:
            j = i
            while j < n and idle[j]:
                j += 1
            if (j - i) >= MIN_IDLE_SEC * FPS:
                blocks.append((round(i / FPS, 1), round(j / FPS, 1)))
            i = j
        else:
            i += 1

    print("idle blocks (start_s, end_s):")
    for s, e in blocks:
        print("  %7.1f %7.1f  (%5.1f s)" % (s, e, e - s))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"duration": total, "blocks": blocks}, f, ensure_ascii=False)
    print("saved", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
