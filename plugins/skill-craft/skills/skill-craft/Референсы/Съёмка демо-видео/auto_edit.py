# -*- coding: utf-8 -*-
"""Автомонтаж демо-ролика по журналу событий (DEMO-VIDEO.md §4).

Запуск: python auto_edit.py edit.json
Вход:  исходник записи (.webm), events.json (record_events.js или ручная
       разметка), edit.json — сценарий монтажа (образец edit.example.json).
Выход: <output>.mp4 (H.264, основной), <output>.webm (VP9), <output>.vtt,
       <output>_poster.png, <output>_timeline.json (для qa_video.py).

Как строится таймлайн:
- всё до события start_at вырезается (загрузка, списки пространств);
- holds — ключевые моменты на 1x, с плавным зумом к рамке события;
- между holds: статичные участки (экран стоит, агент думает) сжимаются
  до max_compressed секунд с бейджем «×N», участки с движением — ×active;
- титульная и финальная карточки — в фирменных цветах, шрифт SB Sans
  (или Arial); главы — плашка сверху слева, callouts — плашка снизу.

Грабли (те же, что в make_subtitles прошлой версии): абсолютные
Windows-пути внутри filtergraph недопустимы — ffmpeg запускается с
cwd=рабочая папка, шрифт и тексты передаются относительными именами;
тексты — во внешних файлах utf-8-sig, expansion=none.
"""
import json
import os
import shutil
import subprocess
import sys

import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand_cards  # noqa: E402  фирменные карточки GigaCowork

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 25
MOTION_FPS = 4          # частота анализа движения
STATIC_TH = 0.02        # кадр «стоит», если изменилось < 2% пикселей
DIFF = 30               # порог отличия пикселя
MW, MH = 64, 36         # кадр анализа движения

# цвета GigaCowork (gigacowork.css)
C_BG, C_TEXT, C_MUTED, C_TEAL = "0xF5F7FA", "0x121212", "0x6B6966", "0x13B3A7"

DEFAULTS = {
    "size": [1920, 1080],
    "start_at": "start",
    "start_pre": 0.3,
    "end_at": None,
    "end_post": 6.0,
    "sync_offset": 0.0,
    "speed": {"idle": 20, "active": 3, "max_compressed": 1.5},
    "chapter_dur": 4.0,
    "callout_dur": 3.0,
    "music": None,
    "music_db": -20,
}


def die(msg):
    sys.exit("auto_edit: " + msg)


def read_exact(stream, n):
    buf = b""
    while len(buf) < n:
        chunk = stream.read(n - len(buf))
        if not chunk:
            return buf
        buf += chunk
    return buf


def duration(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    for line in r.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split(",")[0].split()[1].split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    die("не удалось определить длительность " + path)


def motion(path):
    """Доля изменившихся пикселей для каждого шага 1/MOTION_FPS."""
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-an", "-i", path,
           "-vf", "fps=%d,scale=%d:%d" % (MOTION_FPS, MW, MH),
           "-pix_fmt", "gray", "-f", "rawvideo", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out, prev, n = [], None, MW * MH
    while True:
        buf = read_exact(proc.stdout, n)
        if len(buf) < n:
            break
        out.append(1.0 if prev is None else sum(1 for a, b in zip(prev, buf) if abs(a - b) > DIFF) / n)
        prev = buf
    proc.wait()
    return out


def load_events(cfg, base):
    path = os.path.join(base, cfg.get("events", "events.json"))
    data = json.load(open(path, encoding="utf-8"))
    evs = data.get("events", []) if isinstance(data, dict) else data
    start_ms = data.get("video_start_ms") if isinstance(data, dict) else None
    for e in evs:
        if "t" not in e:
            if start_ms is None or "ts" not in e:
                die("событие без t и без ts/video_start_ms: %r" % e)
            e["t"] = (e["ts"] - start_ms) / 1000.0
        e["t"] = float(e["t"]) + cfg["sync_offset"]
    return sorted(evs, key=lambda e: e["t"])


def find(events, ref):
    """ref = 'type' (первое) или 'type#n' (n-е по счёту)."""
    name, _, idx = ref.partition("#")
    found = [e for e in events if e["type"] == name]
    k = int(idx) - 1 if idx else 0
    if k >= len(found):
        die("нет события %r; есть: %s" % (ref, ", ".join(sorted({e['type'] for e in events}))))
    return found[k]


def center(ev):
    b = ev.get("box")
    if not b or not b.get("vw"):
        return 0.5, 0.5
    return (b["x"] + b["w"] / 2) / b["vw"], (b["y"] + b["h"] / 2) / b["vh"]


def gap_segments(a, b, mot, sp):
    """Разбить промежуток [a, b) на статичные и активные отрезки."""
    if b - a < 0.05:
        return []
    runs = []
    i0, i1 = int(a * MOTION_FPS), max(int(a * MOTION_FPS) + 1, int(b * MOTION_FPS))
    for i in range(i0, i1):
        static = i < len(mot) and mot[i] < STATIC_TH
        t0, t1 = max(a, i / MOTION_FPS), min(b, (i + 1) / MOTION_FPS)
        if runs and runs[-1][2] == static:
            runs[-1][1] = t1
        else:
            runs.append([t0, t1, static])
    # короткие «стоячие» куски (< 0.75 с) — часть активного участка
    for r in runs:
        if r[2] and r[1] - r[0] < 0.75:
            r[2] = False
    merged = []
    for r in runs:
        if merged and merged[-1][2] == r[2]:
            merged[-1][1] = r[1]
        else:
            merged.append(list(r))
    # короткие всплески движения (< 1 с) внутри ожидания — тоже ожидание:
    # иначе скорость дёргается ×20 → ×3 → ×20 на долях секунды
    for k in range(1, len(merged) - 1):
        r = merged[k]
        if not r[2] and r[1] - r[0] < 1.0 and merged[k - 1][2] and merged[k + 1][2]:
            r[2] = True
    again = []
    for r in merged:
        if again and again[-1][2] == r[2]:
            again[-1][1] = r[1]
        else:
            again.append(list(r))
    merged = again
    segs = []
    for s, e, static in merged:
        ln = e - s
        if static:
            speed = max(sp["idle"], ln / sp["max_compressed"])
            segs.append({"src": [s, e], "speed": speed, "kind": "static"})
        else:
            segs.append({"src": [s, e], "speed": float(sp["active"]), "kind": "active"})
    return segs


def build_timeline(cfg, events, dur, mot):
    S = 0.0
    if cfg["start_at"]:
        S = max(0.0, find(events, cfg["start_at"])["t"] - cfg["start_pre"])
    E = dur
    if cfg["end_at"]:
        E = min(dur, find(events, cfg["end_at"])["t"] + cfg["end_post"])
    holds = []
    for h in cfg.get("holds", []):
        ev = find(events, h["at"])
        s, e = max(S, ev["t"] - h.get("pre", 0.5)), min(E, ev["t"] + h.get("post", 3.0))
        cx, cy = h.get("center") or center(ev)
        holds.append({"src": [s, e], "speed": float(h.get("speed", 1.0)), "kind": "hold", "label": h["at"],
                      "zoom": float(h.get("zoom", 1.0)), "c": [cx, cy]})
    holds.sort(key=lambda h: h["src"][0])
    clean = []
    for h in holds:
        if clean and h["src"][0] < clean[-1]["src"][1]:
            h["src"][0] = clean[-1]["src"][1]
        if h["src"][1] - h["src"][0] >= 0.3:
            clean.append(h)
    # cut — вырезаемые куски исходника (простой после ответа агента и т.п.):
    # склейка без ускорения и без бейджа
    cuts = sorted((float(a), float(b)) for a, b in cfg.get("cut", []))

    def gap(a, b):
        out = []
        for ca, cb in cuts:
            if cb <= a or ca >= b:
                continue
            out += gap_segments(a, max(a, ca), mot, cfg["speed"])
            a = max(a, cb)
        return out + gap_segments(a, b, mot, cfg["speed"])

    segs, cur = [], S
    for h in clean:
        segs += gap(cur, h["src"][0])
        segs.append(h)
        cur = h["src"][1]
    segs += gap(cur, E)
    out = [s for s in segs if (s["src"][1] - s["src"][0]) / s["speed"] >= 1.0 / FPS]
    return out


def write_text(work, name, text):
    with open(os.path.join(work, name), "w", encoding="utf-8-sig") as f:
        f.write(text)
    return name


def dt(textfile, size, color, x, y, box=None, extra=""):
    s = "drawtext=fontfile=font.ttf:textfile=%s:expansion=none:fontsize=%d:fontcolor=%s:x=%s:y=%s" % (
        textfile, size, color, x, y)
    if box:
        s += ":box=1:boxcolor=%s:boxborderw=%d" % box
    return s + extra


def fade_alpha(a, b, f=0.3):
    return ":alpha='if(lt(t,%.3f),(t-%.3f)/%.2f,if(gt(t,%.3f),(%.3f-t)/%.2f,1))':enable='between(t,%.3f,%.3f)'" % (
        a + f, a, f, b - f, b, f, a, b)


def camera_keyframes(segs, t0, cfg):
    """Ключевые кадры «виртуальной камеры» (время тела ролика, zoom, cx, cy).

    Зум — только на акцентах (holds с zoom > 1). Наезд начинается за `lead`
    до акцента и длится `move` с; соседние акценты (зазор < `chain_gap`)
    связываются переездом без отъезда; отъезд — `move` с после конца акцента.
    """
    cam = dict({"move": 1.1, "lead": 0.35, "chain_gap": 1.8}, **cfg.get("camera", {}))
    acc = [(s["out"][0] - t0, s["out"][1] - t0, s["zoom"], s["c"][0], s["c"][1])
           for s in segs if s["kind"] == "hold" and s.get("zoom", 1.0) > 1.01]
    kf = [[0.0, 1.0, 0.5, 0.5]]
    for i, (a, b, z, cx, cy) in enumerate(acc):
        # дальний переезд — дольше: 1.1 с на соседнюю область, до 1.8 с через весь кадр
        pz, px, py = kf[-1][1:]
        dist = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5 + abs(z - pz) * 0.3
        mv = min(1.8, max(cam["move"], 0.9 + 1.6 * dist))
        st = max(kf[-1][0], a - cam["lead"] - (mv - cam["move"]) / 2)
        en = min(st + mv, max(st + 0.5, b))
        kf.append([st] + kf[-1][1:])
        kf.append([en, z, cx, cy])
        nxt = acc[i + 1] if i + 1 < len(acc) else None
        if nxt and nxt[0] - b < cam["chain_gap"]:
            continue                      # держим кадр до переезда к следующему акценту
        kf.append([max(b, en), z, cx, cy])
        kf.append([max(b, en) + cam["move"], 1.0, cx, cy])
    for k in range(1, len(kf)):           # строго возрастающее время
        kf[k][0] = max(kf[k][0], kf[k - 1][0] + 0.04)
    return kf


def camera_expr(kfs):
    """Кусочная интерполяция smootherstep → выражения zoom, x, y для zoompan."""
    def piece(idx):
        expr = "%.4f" % kfs[-1][idx]
        for k in range(len(kfs) - 2, -1, -1):
            t0, t1 = kfs[k][0], kfs[k + 1][0]
            v0, v1 = kfs[k][idx], kfs[k + 1][idx]
            if abs(v1 - v0) < 1e-6:
                seg = "%.4f" % v0
            else:
                p = "clip((ot-%.3f)/%.3f,0,1)" % (t0, t1 - t0)
                seg = "%.4f+(%.4f)*(%s)*(%s)*(%s)*((%s)*((%s)*6-15)+10)" % (v0, v1 - v0, p, p, p, p, p)
            expr = "if(lt(ot,%.3f),%s,%s)" % (t1, seg, expr)
        return expr
    z = piece(1)
    x = "clip((%s)*iw-iw/zoom/2,0,iw-iw/zoom)" % piece(2)
    y = "clip((%s)*ih-ih/zoom/2,0,ih-ih/zoom)" % piece(3)
    return z, x, y


def main():
    if len(sys.argv) < 2:
        die("использование: python auto_edit.py edit.json")
    cfg_path = os.path.abspath(sys.argv[1])
    base = os.path.dirname(cfg_path)
    cfg = dict(DEFAULTS)
    cfg.update(json.load(open(cfg_path, encoding="utf-8")))
    cfg["speed"] = dict(DEFAULTS["speed"], **cfg.get("speed", {}))
    W, H = cfg["size"]
    src = os.path.join(base, cfg["source"])
    out_base = os.path.join(base, cfg.get("output", "demo"))
    work = os.path.join(base, "_edit")
    os.makedirs(work, exist_ok=True)

    font = cfg.get("font")
    candidates = [font] if font else []
    candidates += [os.path.join(HERE, "..", "Сборка HTML агента", "SBSansDisplay-Regular.ttf"),
                   r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    font = next((p for p in candidates if p and os.path.exists(p)), None)
    if not font:
        die("не найден шрифт: укажите font в edit.json")
    shutil.copyfile(font, os.path.join(work, "font.ttf"))

    events = load_events(cfg, base)
    dur = duration(src)
    print("исходник %.1f с, событий %d; анализ движения…" % (dur, len(events)))
    mot = motion(src)
    segs = build_timeline(cfg, events, dur, mot)

    title, end = cfg.get("title"), cfg.get("end")
    t_title = float(title.get("dur", 3)) if title else 0.0
    t_end = float(end.get("dur", 5)) if end else 0.0

    # время на выходе для каждого сегмента
    t = t_title
    for s in segs:
        s["out"] = [t, t + (s["src"][1] - s["src"][0]) / s["speed"]]
        t = s["out"][1]
    body_end = t
    total = body_end + t_end

    def out_time(src_t):
        for s in segs:
            if s["src"][0] <= src_t <= s["src"][1]:
                return s["out"][0] + (src_t - s["src"][0]) / s["speed"]
        later = [s for s in segs if s["src"][0] > src_t]
        return later[0]["out"][0] if later else body_end

    fs_badge, fs_chap, fs_call = int(H * 0.026), int(H * 0.030), int(H * 0.034)
    chains, labels = [], []
    scale = "scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=white"

    # входы: 0 — запись, далее PNG-карточки, последним — музыка
    inputs = ["-i", src]
    n_in = 1

    def card(png, dur, label, fade):
        """Фирменная карточка (PNG) с медленным наездом камеры 1.00 → 1.04."""
        nonlocal n_in
        inputs.extend(["-loop", "1", "-framerate", str(FPS), "-t", "%.3f" % dur, "-i", png])
        n = max(1, int(round(dur * FPS)))
        chains.append(("[%d:v]scale=%d:%d:flags=lanczos,zoompan=z='1+0.04*on/%d':x='iw/2-iw/zoom/2':"
                       "y='ih/2-ih/zoom/2':d=1:s=%dx%d:fps=%d,%s,format=yuv420p,setsar=1[%s]")
                      % (n_in, W * 2, H * 2, n, W, H, FPS, fade, label))
        labels.append("[%s]" % label)
        n_in += 1

    font_path = brand_cards.find_font(cfg.get("font"))
    if title:
        png = os.path.join(work, "title.png")
        brand_cards.render_title(title, W, H, font_path, png)
        card(png, t_title, "ct", "fade=t=out:st=%.2f:d=0.4:color=white" % (t_title - 0.4))

    # тело ролика: сегменты без зума → одна склейка → одна «виртуальная камера»
    body = []
    for i, s in enumerate(segs):
        a, b = s["src"]
        ch = "[0:v]trim=start=%.3f:end=%.3f,setpts=(PTS-STARTPTS)/%.4f,fps=%d" % (a, b, s["speed"], FPS)
        chains.append(ch + "," + (scale % (W, H, W, H)) + ",format=yuv420p,setsar=1[v%d]" % i)
        body.append("[v%d]" % i)
    chains.append("%sconcat=n=%d:v=1:a=0[body]" % ("".join(body), len(body)))
    kfs = camera_keyframes(segs, t_title, cfg)
    if len(kfs) > 1:
        z_e, x_e, y_e = camera_expr(kfs)
        chains.append(("[body]scale=%d:%d:flags=lanczos,zoompan=z='%s':x='%s':y='%s':d=1:s=%dx%d:fps=%d,"
                       "format=yuv420p,setsar=1[bodycam]") % (W * 2, H * 2, z_e, x_e, y_e, W, H, FPS))
        labels.append("[bodycam]")
    else:
        labels.append("[body]")

    if end:
        png = os.path.join(work, "end.png")
        brand_cards.render_end(end, W, H, font_path, png)
        card(png, t_end, "ce", "fade=t=in:st=0:d=0.4:color=white")

    chains.append("%sconcat=n=%d:v=1:a=0[cat]" % ("".join(labels), len(labels)))

    # главы и плашки поверх склейки
    over, cues = [], []
    chapters = sorted(((out_time(find(events, c["at"])["t"]), c["text"]) for c in cfg.get("chapters", [])))
    for k, (a, text) in enumerate(chapters):
        b = min(a + cfg["chapter_dur"], chapters[k + 1][0] if k + 1 < len(chapters) else body_end, body_end)
        if b - a < 0.8:
            continue
        f = write_text(work, "chap%02d.txt" % k, text)
        over.append(dt(f, fs_chap, "white", "48", "40", ("0x121212@0.82", 18), fade_alpha(a, b)))
        cues.append((a, b, text))
    for k, c in enumerate(cfg.get("callouts", [])):
        a = out_time(find(events, c["at"])["t"]) + float(c.get("delay", 0.4))
        b = min(a + float(c.get("dur", cfg["callout_dur"])), body_end)
        if b - a < 0.8:
            continue
        f = write_text(work, "call%02d.txt" % k, c["text"])
        over.append(dt(f, fs_call, "white", "(w-tw)/2", "h-th-%d" % int(H * 0.08),
                       (C_TEAL + "@0.95", 20), fade_alpha(a, b)))
        cues.append((a, b, c["text"]))
    # субтитры — реплики в секундах итогового ролика (как voiceover.json):
    # "subtitles": "voiceover.json" или [{start, end, text}]; поверх карточек не рисуются
    subs = cfg.get("subtitles")
    if isinstance(subs, str):
        subs = json.load(open(os.path.join(base, subs), encoding="utf-8"))["slots"]
    for k, sb in enumerate(subs or []):
        if "at" in sb:   # привязка к событию: {"at": "send", "delay": 0.3, "dur": 3.5, "text": ...}
            a0 = out_time(find(events, sb["at"])["t"]) + float(sb.get("delay", 0.2))
            sb = dict(sb, start=a0, end=a0 + float(sb.get("dur", 3.5)))
        a, b = max(float(sb["start"]), t_title), min(float(sb["end"]), body_end)
        if b - a < 0.8:
            continue
        f = write_text(work, "sub%02d.txt" % k, sb["text"])
        over.append(dt(f, int(H * 0.031), "white", "(w-tw)/2", "h-th-%d" % int(H * 0.07),
                       (cfg.get("subtitle_color", "0x2E9FD8@0.92"), 20), fade_alpha(a, b, 0.3)))
        cues.append((a, b, sb["text"]))
    # бейдж «Ускорено ×N» — один на каждый непрерывный ускоренный отрезок
    fast, run = [], []
    for s in segs + [None]:
        if s is not None and s["kind"] != "hold" and s["speed"] >= 2:
            run.append(s)
            continue
        if run:
            a, b = run[0]["out"][0], run[-1]["out"][1]
            src_len = sum(x["src"][1] - x["src"][0] for x in run)  # без вырезанных кусков
            if b - a >= 0.6 and src_len / (b - a) >= 6:
                fast.append((a, b, src_len / (b - a)))
            run = []
    for k, (a, b, sp) in enumerate(fast if cfg.get("badge", False) else []):  # бейдж — только по явному "badge": true
        f = write_text(work, "badge%02d.txt" % k, "Ускорено ×%d" % round(sp) if sp <= 60 else "Ускорено")
        over.append(dt(f, fs_badge, "white", "w-tw-48", "40", ("0x121212@0.6", 14),
                       ":enable='between(t,%.3f,%.3f)'" % (a, b)))
    chains.append("[cat]" + (",".join(over) if over else "null") + ",split=2[vm][vw]")

    music = cfg.get("music")
    if music:
        inputs += ["-i", os.path.join(base, music)]
        chains.append("[%d:a]atrim" % n_in + "=0:%.3f,asetpts=PTS-STARTPTS,volume=%ddB,afade=t=in:d=1,"
                      "afade=t=out:st=%.3f:d=2,asplit=2[am][aw]" % (total, cfg["music_db"], total - 2))

    graph = os.path.join(work, "graph.txt")
    with open(graph, "w", encoding="utf-8") as f:
        f.write(";\n".join(chains))

    mp4, webm = out_base + ".mp4", out_base + ".webm"
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-y"] + inputs + ["-/filter_complex", "graph.txt"]
    cmd += ["-map", "[vm]"] + (["-map", "[am]", "-c:a", "aac", "-b:a", "128k"] if music else ["-an"])
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4]
    cmd += ["-map", "[vw]"] + (["-map", "[aw]", "-c:a", "libopus", "-b:a", "96k"] if music else ["-an"])
    cmd += ["-c:v", "libvpx-vp9", "-crf", "33", "-b:v", "0", "-row-mt", "1", "-deadline", "good",
            "-cpu-used", "4", webm]
    print("сегментов %d, длительность ролика %.1f с; рендер…" % (len(segs), total))
    r = subprocess.run(cmd, cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-4000:])
        die("ffmpeg завершился с ошибкой (граф — %s)" % graph)

    poster_t = (body_end + total) / 2 if end else max(0.0, body_end - 1)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % poster_t, "-i", mp4,
                    "-frames:v", "1", out_base + "_poster.png"], check=True)

    def ts(x):
        return "%02d:%02d:%06.3f" % (x // 3600, x % 3600 // 60, x % 60)
    with open(out_base + ".vtt", "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for k, (a, b, text) in enumerate(sorted(cues), 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (k, ts(a), ts(b), text))

    timeline = {"duration": total, "title": [0, t_title], "end": [body_end, total],
                "segments": [{k: s[k] for k in ("src", "out", "speed", "kind") if k in s} | {"label": s.get("label")}
                             for s in segs]}
    json.dump(timeline, open(out_base + "_timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("OK: %s (%.1f с, %.1f МБ)" % (mp4, total, os.path.getsize(mp4) / 1e6))
    print("    %s, %s.vtt, %s_poster.png, %s_timeline.json" % (webm, out_base, out_base, out_base))
    if not 40 <= total <= 100:
        print("ВНИМАНИЕ: длительность %.0f с вне 40–100 с — поправьте holds/speed" % total)


if __name__ == "__main__":
    main()
