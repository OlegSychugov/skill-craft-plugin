# -*- coding: utf-8 -*-
"""Приёмка демо-ролика (DEMO-VIDEO.md §6): автоматические проверки + раскадровка.

Запуск: python qa_video.py ролик.mp4 [ролик_timeline.json]
Выход:  <ролик>_qa/qa_report.md и <ролик>_qa/sheet_NN.png — листы раскадровки
        (кадр каждые 2 с, таймкод на кадре). Листы агент ОБЯЗАН просмотреть
        сам (Read изображения) и пройти визуальный чек-лист из отчёта:
        автоматика не видит чужие пространства, служебные файлы и перекрытия.
Код возврата: 0 — автоматические проверки пройдены, 1 — есть FAIL.

Без timeline.json статичные участки проверяются по всему ролику; с ним —
только вне holds и карточек (там статика допустима).
"""
import json
import os
import re
import shutil
import subprocess
import sys

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, W, H = 4, 64, 36
STATIC_TH, DIFF = 0.02, 30
MAX_STATIC = 3.0          # с — дольше без движения вне holds нельзя
DUR_RANGE = (60, 100)     # с
MAX_MB = 20


def read_exact(stream, n):
    buf = b""
    while len(buf) < n:
        chunk = stream.read(n - len(buf))
        if not chunk:
            return buf
        buf += chunk
    return buf


def probe(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace").stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r)
    v = re.search(r"Video: (\w+).*?, (\d{3,5})x(\d{3,5})", r)
    return {"duration": int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]) if d else 0.0,
            "codec": v[1] if v else "?", "w": int(v[2]) if v else 0, "h": int(v[3]) if v else 0,
            "audio": "Audio:" in r}


def frames(path):
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-an", "-i", path,
           "-vf", "fps=%d,scale=%d:%d" % (FPS, W, H), "-pix_fmt", "gray", "-f", "rawvideo", "pipe:1"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out = []
    while True:
        b = read_exact(p.stdout, W * H)
        if len(b) < W * H:
            break
        out.append(b)
    p.wait()
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("использование: python qa_video.py ролик.mp4 [ролик_timeline.json]")
    video = os.path.abspath(sys.argv[1])
    tl = json.load(open(sys.argv[2], encoding="utf-8")) if len(sys.argv) > 2 else None
    qa = os.path.splitext(video)[0] + "_qa"
    os.makedirs(qa, exist_ok=True)

    info = probe(video)
    size_mb = os.path.getsize(video) / 1e6
    fr = frames(video)
    checks = []

    def check(ok, name, detail):
        checks.append(("PASS" if ok else "FAIL", name, detail))

    check(DUR_RANGE[0] <= info["duration"] <= DUR_RANGE[1], "Длительность",
          "%.1f с (норма %d–%d)" % (info["duration"], *DUR_RANGE))
    check(info["codec"] == "h264", "Формат для клиента", "кодек %s (нужен MP4 H.264)" % info["codec"])
    check(info["h"] >= 1080, "Разрешение", "%dx%d (нужно ≥ 1920x1080)" % (info["w"], info["h"]))
    check(size_mb <= MAX_MB, "Размер файла", "%.1f МБ (≤ %d)" % (size_mb, MAX_MB))

    if fr:
        first = fr[0]
        mean = sum(first) / len(first)
        spread = max(first) - min(first)
        check(not (mean > 235 and spread < 40), "Первый кадр", "яркость %.0f, контраст %d (белый/пустой кадр — FAIL)" % (mean, spread))

    allowed = []
    if tl:
        allowed += [tl["title"], tl["end"]]
        allowed += [s["out"] for s in tl["segments"] if s["kind"] == "hold"]

    def in_allowed(a, b):
        return any(a >= x - 0.3 and b <= y + 0.3 for x, y in allowed)

    blocks, start = [], None
    for i in range(1, len(fr) + 1):
        static = i < len(fr) and sum(1 for a, b in zip(fr[i - 1], fr[i]) if abs(a - b) > DIFF) / (W * H) < STATIC_TH
        t = i / FPS
        if static and start is None:
            start = t
        elif not static and start is not None:
            if t - start > MAX_STATIC and not in_allowed(start, t):
                blocks.append((start, t))
            start = None
    check(not blocks, "Нет «висящих» участков",
          "статика > %.0f с вне holds: %s" % (MAX_STATIC, ", ".join("%.1f–%.1f" % b for b in blocks) or "нет"))

    # раскадровка с таймкодами: кадр каждые 2 с, лист 4x3
    font = os.path.join(qa, "font.ttf")
    for p in (os.path.join(HERE, "..", "Сборка HTML агента", "SBSansDisplay-Regular.ttf"), r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(p):
            shutil.copyfile(p, font)
            break
    for old in os.listdir(qa):
        if old.startswith("sheet_"):
            os.remove(os.path.join(qa, old))
    vf = "fps=0.5,scale=480:270"
    if os.path.exists(font):
        vf += (",drawtext=fontfile=font.ttf:text='%{pts\\:hms}':fontsize=18:fontcolor=white"
               ":box=1:boxcolor=black@0.6:boxborderw=4:x=6:y=6")
    vf += ",tile=4x3"
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-vf", vf,
                    "sheet_%02d.png"], cwd=qa, check=True)
    sheets = sorted(x for x in os.listdir(qa) if x.startswith("sheet_"))

    ok = all(c[0] == "PASS" for c in checks)
    lines = ["# QA ролика %s" % os.path.basename(video), "",
             "Автоматика: **%s**" % ("PASS" if ok else "FAIL"), "",
             "| Статус | Проверка | Детали |", "|---|---|---|"]
    lines += ["| %s | %s | %s |" % c for c in checks]
    lines += ["", "## Визуальный чек-лист (по листам раскадровки)", "",
              "Листы: " + ", ".join(sheets) + " — каждый кадр подписан таймкодом.", "",
              "- [ ] Первый кадр — внутри демо-пространства: нет списка пространств, экранов загрузки.",
              "- [ ] В кадре нет чужих пространств, клиентов, имён людей, личных аватаров.",
              "- [ ] В «Документах» нет служебных файлов (.pkl, .json-кэш, temp).",
              "- [ ] Каждый созданный агентом файл открыт и показан (холст/превью), задержка ≥ 3 с.",
              "- [ ] Итоговые цифры читаются (зум) и совпадают с ответом агента.",
              "- [ ] Главы и плашки не перекрывают результат; текст без опечаток, факты верны.",
              "- [ ] Нет сцен отладки агента (ошибка → исправление) — их вырезают.",
              "- [ ] Демо-данные правдоподобны: без «Ромашек», брендов и ФИО (DEMO-VIDEO.md §2).",
              "- [ ] Есть титульная и финальная карточки; на финальной — «данные вымышлены».", ""]
    with open(os.path.join(qa, "qa_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    for c in checks:
        print("%s  %s — %s" % c)
    print("Отчёт: %s\nЛисты раскадровки (просмотреть!): %s" % (os.path.join(qa, "qa_report.md"), ", ".join(sheets)))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
