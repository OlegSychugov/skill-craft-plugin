# -*- coding: utf-8 -*-
"""Упаковка навыка в ZIP для загрузки на демо-стенд Cowork.

Запуск: python pack_skill.py <папка_навыка> [<папка_для_zip>]
Выход:  <alias>.zip, внутри — корневая папка <alias>/ с SKILL.md и ресурсами.

Почему не tar и не Compress-Archive:
- Compress-Archive пишет пути с «\\» — стенд отвергает их
  («Обратная косая черта в пути запрещена»);
- bsdtar на Windows пишет кириллические имена (Референсы/) в кодировке
  консоли без флага UTF-8 — на стенде имена превращаются в мусор.
zipfile пишет «/» и ставит флаг UTF-8 (0x800) для не-ASCII имён; скрипт
это проверяет и падает с кодом 1, если флага нет.
"""
import os
import sys
import zipfile

SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {".DS_Store", "Thumbs.db"}


def pack(skill_dir, out_dir):
    skill_dir = os.path.abspath(skill_dir)
    alias = os.path.basename(skill_dir.rstrip("\\/"))
    if not os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
        sys.exit("Нет SKILL.md в %s" % skill_dir)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, alias + ".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if name in SKIP_FILES or name.endswith(".pyc"):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, os.path.dirname(skill_dir)).replace("\\", "/")
                z.write(full, rel)
    bad = []
    with zipfile.ZipFile(out) as z:
        for info in z.infolist():
            if "\\" in info.filename:
                bad.append(info.filename + " (обратная косая черта)")
            if not info.filename.isascii() and not info.flag_bits & 0x800:
                bad.append(info.filename + " (нет флага UTF-8)")
        count = len(z.infolist())
    if bad:
        print("FAIL:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print("OK: %s (%d файлов)" % (out, count))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pack(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")
