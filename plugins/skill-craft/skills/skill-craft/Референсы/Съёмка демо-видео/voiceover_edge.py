# -*- coding: utf-8 -*-
"""Озвучка демо-ролика без API-ключей: Edge TTS + обработка звука (DEMO-VIDEO.md §5).

Запуск: python voiceover_edge.py voiceover.json [--voice Svetlana|Dmitry] [--video ролик.mp4]
Вход:  voiceover.json — {"video": "...mp4", "slots": [{"start", "end", "text"}, ...]}
       (тайминги — секунды итогового ролика, из *_timeline.json).
Выход: _voice_<голос>/slot_NN.wav, voice_full.wav, report.md и
       <ролик>_voice_<голос>.mp4 — видео без перекодирования + дорожка AAC.

Что делается для натуральности:
- текст под голос: числа словами пишет автор, скрипт расставляет ударения в
  брендах (SAY) и разворачивает аббревиатуры;
- синтез по одной реплике; темп подбирается так, чтобы реплика легла в слот
  без спешки (от −6% до +10%), иначе — FAIL с просьбой сократить текст;
- обработка: срез НЧ, тёплый подъём 180 Гц, мягкий спад резкости 6–7 кГц,
  лёгкая компрессия, едва заметная «комната» вместо стерильной сухости,
  громкость −16 LUFS.
Edge TTS — онлайн-сервис Microsoft без официальной коммерческой лицензии:
для клиентских материалов это синтетический голос с оговоркой (report.md).
"""
import asyncio
import json
import time
import os
import subprocess
import sys

import edge_tts
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
VOICES = {"svetlana": "ru-RU-SvetlanaNeural", "dmitry": "ru-RU-DmitryNeural"}
RATES = [-6, -3, 0, 3, 6, 10]          # %: от спокойного к быстрому
SAY = {                                  # произношение: ударение — U+0301
    "GigaCowork": "Гига Ково́рк",
    "ИИ-": "И-И ",
    "Excel": "Эксель",
}
POST = ("highpass=f=70,equalizer=f=180:t=q:w=1.2:g=2.5,equalizer=f=6500:t=q:w=1.5:g=-2.5,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=12:release=220:makeup=2,"
        "aecho=0.8:0.88:24|37:0.10|0.06")


def say(text):
    for k, v in SAY.items():
        text = text.replace(k, v)
    return text


def dur(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace").stderr
    for ln in r.splitlines():
        if "Duration:" in ln:
            h, m, s = ln.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


async def synth(text, voice, rate, mp3):
    await edge_tts.Communicate(text, voice, rate="%+d%%" % rate).save(mp3)


def clean(mp3, wav):
    """48 кГц моно, тишина по краям срезана."""
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", mp3, "-af", af,
                    "-ar", "48000", "-ac", "1", wav], check=True)
    return dur(wav)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("использование: python voiceover_edge.py voiceover.json [--voice Svetlana|Dmitry] [--video x.mp4]")
    cfg_path = os.path.abspath(args[0])
    base = os.path.dirname(cfg_path)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    vkey = (args[args.index("--voice") + 1] if "--voice" in args else "svetlana").lower()
    voice = VOICES[vkey]
    video = os.path.join(base, args[args.index("--video") + 1] if "--video" in args else cfg["video"])
    total = dur(video)
    out = os.path.join(base, "_voice_" + vkey)
    os.makedirs(out, exist_ok=True)

    rows, fails = [], []
    for i, s in enumerate(cfg["slots"], 1):
        slot = s["end"] - s["start"] - 0.15
        text = say(s["text"])
        chosen = None
        for rate in RATES:
            mp3 = os.path.join(out, "slot_%02d.mp3" % i)
            for attempt in range(4):
                try:
                    asyncio.run(synth(text, voice, rate, mp3))
                    break
                except Exception:  # сбой сервиса — пауза и повтор
                    if attempt == 3:
                        raise
                    time.sleep(3 + 3 * attempt)
            wav = os.path.join(out, "slot_%02d.wav" % i)
            d = clean(mp3, wav)
            os.remove(mp3)
            if d <= slot:
                chosen = (rate, d)
                break
        if chosen is None:
            fails.append(i)
            chosen = (RATES[-1], d)
        rows.append((i, s["start"], s["end"], chosen[0], chosen[1], s["text"]))
        print("slot %d: %+d%%, %.2f с из %.2f %s" % (i, chosen[0], chosen[1], slot, "OK" if i not in fails else "НЕ ВЛЕЗАЕТ"))

    # сборка дорожки: реплики на своих start, обработка, −16 LUFS, ровно по длине видео
    inputs, chains, mix = [], [], ""
    for k, (i, st, *_r) in enumerate(rows):
        inputs += ["-i", os.path.join(out, "slot_%02d.wav" % i)]
        chains.append("[%d:a]adelay=%d:all=1[a%d]" % (k, int(st * 1000), k))
        mix += "[a%d]" % k
    fc = ";".join(chains) + ";%samix=inputs=%d:normalize=0,%s,apad,atrim=0:%.3f,loudnorm=I=-16:TP=-1.5:LRA=7[v]" % (
        mix, len(rows), POST, total)
    full = os.path.join(out, "voice_full.wav")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y"] + inputs +
                   ["-filter_complex", fc, "-map", "[v]", "-ar", "48000", "-ac", "1", full], check=True)

    dst = os.path.splitext(video)[0] + "_voice_" + vkey + ".mp4"
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-i", full,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", dst], check=True)

    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("# Озвучка: %s\n\nДвижок: Edge TTS (Microsoft, онлайн, без ключа). Голос синтетический — "
                "для клиентских материалов указывать «озвучено синтезатором речи»; официальной коммерческой "
                "лицензии у Edge TTS нет.\n\n| # | Слот, с | Темп | Длина, с | Текст |\n|---|---|---|---|---|\n" % voice)
        for i, st, en, rate, d, t in rows:
            f.write("| %d | %.1f–%.1f | %+d%% | %.2f | %s |\n" % (i, st, en, rate, d, t))
        if fails:
            f.write("\n**Не влезают в слот:** %s — сократить текст.\n" % ", ".join(map(str, fails)))
    print("OK:", dst)
    if fails:
        print("ВНИМАНИЕ: не влезают реплики", fails, "— сократите текст")
        sys.exit(1)


if __name__ == "__main__":
    main()
