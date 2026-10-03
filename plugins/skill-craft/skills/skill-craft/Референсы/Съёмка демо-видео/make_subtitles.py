# -*- coding: utf-8 -*-
"""Субтитры для демо-видео: вшитые (drawtext) + мягкие (.vtt) из одного списка.

Запуск: python make_subtitles.py [видео.webm]
Рядом с видео создаются: <имя>_subtitled.webm и <имя>.vtt.

Грабли, учтённые в реализации:
- абсолютные Windows-пути внутри filtergraph недопустимы (двоеточие `C:`
  рвёт парсер опций) — ffmpeg запускается с cwd=CAPS_DIR, шрифт и титры
  передаются по относительным именам;
- текст тирируется во внешний файл в utf-8-sig (BOM) — надёжная кириллица;
- имя файла титра подставляется шаблоном {n:02d} (.format), не %02d.
"""
import os
import subprocess
import sys

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SRC = sys.argv[1] if len(sys.argv) > 1 else "input.webm"
BASE, _ = os.path.splitext(SRC)
DST = BASE + "_subtitled.webm"
VTT = BASE + ".vtt"

CAPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_caps")
FONT = "font.ttf"  # копия .ttf в CAPS_DIR (ASCII-имя)

# (start, end, текст) — тайминги в СЕКУНДАХ ИТОГОВОГО РОЛИКА; без `:` и `'`
captions = [
    # (0.0,  2.2,  "Пространство «Финансовый контроль» — аудит заявок на оплату"),
    # (2.2,  6.4,  "Прикрепляем реестр из 8 заявок на оплату"),
    # (6.4,  13.7, "Формулируем задачу — дубли за 90 дней, договоры, лимиты бюджета"),
    # ...
]
if not captions:
    sys.exit("Заполните список captions под таймлайн ролика")

os.makedirs(CAPS_DIR, exist_ok=True)


def ts(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return "%02d:%02d:%06.3f" % (h, m, s)


# --- WebVTT ---
lines = ["WEBVTT", ""]
for i, (a, b, txt) in enumerate(captions, 1):
    lines += ["%d" % i, "%s --> %s" % (ts(a), ts(b)), txt, ""]
with open(VTT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("VTT:", VTT)

# --- drawtext-цепочка ---
draws = []
for i, (a, b, txt) in enumerate(captions):
    tf = os.path.join(CAPS_DIR, "cap%02d.txt" % i)
    with open(tf, "w", encoding="utf-8-sig") as f:
        f.write(txt)
    draws.append(
        "drawtext=fontfile={font}:textfile=cap{n:02d}.txt:fontsize=23:fontcolor=white:"
        "borderw=2:bordercolor=black@0.85:box=1:boxcolor=black@0.45:boxborderw=14:"
        "x=(w-text_w)/2:y=h-th-42:enable='between(t,{a:.2f},{b:.2f})'".format(
            font=FONT, n=i, a=a, b=b)
    )
fc = "[0:v]" + ",".join(draws) + "[out]"

cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-y", "-i", SRC,
       "-filter_complex", fc, "-map", "[out]",
       "-c:v", "libvpx", "-crf", "12", "-b:v", "2M", "-auto-alt-ref", "0",
       "-an", DST]
r = subprocess.run(cmd, capture_output=True, text=True, cwd=CAPS_DIR)
if r.returncode != 0:
    print(r.stderr[-4000:])
    sys.exit(1)
print("OK:", DST)
