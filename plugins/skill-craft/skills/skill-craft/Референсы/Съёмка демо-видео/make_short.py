# -*- coding: utf-8 -*-
"""Монтаж короткой версии демо: статичные участки ускоряются, ключевые — 1x.

Один проход ffmpeg: для каждого сегмента
    [0:v]trim=start:S:end:E,setpts=(PTS-STARTPTS)/speed[sN]
затем concat -> fps=25 -> libvpx.

Запуск: python make_short.py [исходник.webm] [результат_short.webm]
Таблицу сегментов (start, end, speed, описание) заполните по результатам
analyze_idle.py: длинные статичные блоки — x12–x25, ключевые моменты — 1x.
"""
import subprocess
import sys

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SRC = sys.argv[1] if len(sys.argv) > 1 else "input.webm"
DST = sys.argv[2] if len(sys.argv) > 2 else "output_short.webm"

# (start, end, speed, описание) — времена в СЕКУНДАХ ИСХОДНИКА
segments = [
    # пример из кейса financial-controller (7:15 -> 1:22):
    # (9.3,  11.5,  1,  "Пространство загрузилось"),
    # (11.5, 41.5,  25, "Курсор до меню (ускорено)"),
    # (41.5, 44.5,  1,  "Меню «Прикрепить файл»"),
    # (44.5, 101.0, 20, "Прикрепление файла и ввод запроса (ускорено)"),
    # (101.0, 105.5, 1, "Запрос готов, отправка"),
    # (105.5, 222.5, 16, "Агент: чтение файла, Excel (ускорено)"),
    # (222.5, 228.5, 1, "Прогресс 40%, навыки"),
    # (228.5, 267.5, 16, "Продолжение расчётов (ускорено)"),
    # (267.5, 273.5, 1, "Расчёты готовы, навык Word"),
    # (273.5, 349.5, 16, "Создание заключения Word (ускорено)"),
    # (349.5, 364.0, 1, "Результат: таблица рисков"),
    # (364.0, 412.0, 12, "Просмотр результата (ускорено)"),
    # (412.0, 435.5, 1, "Финал"),
]
if not segments:
    sys.exit("Заполните таблицу segments по результатам analyze_idle.py")

parts, labels = [], []
for i, (s, e, sp, _) in enumerate(segments):
    parts.append("[0:v]trim=start=%.2f:end=%.2f,setpts=(PTS-STARTPTS)/%d[s%d]" % (s, e, sp, i))
    labels.append("[s%d]" % i)
fc = ";".join(parts) + ";%sconcat=n=%d:v=1:a=0[cat];[cat]fps=25[out]" % ("".join(labels), len(segments))

est = sum((e - s) / sp for s, e, sp, _ in segments)
print("segments=%d estimated duration=%.1fs" % (len(segments), est))

cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-y", "-i", SRC,
       "-filter_complex", fc, "-map", "[out]",
       "-c:v", "libvpx", "-crf", "10", "-b:v", "2M", "-auto-alt-ref", "0",
       "-an", DST]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-4000:])
    sys.exit(1)
print("OK:", DST)
