# -*- coding: utf-8 -*-
"""Фирменные карточки ролика в стиле GigaCowork (DEMO-VIDEO.md §4).

Источник стиля — «GigaCowork — примеры разделителей.pptx»:
- титульная карточка = слайд-разделитель: фон с лентами, логотип слева
  вверху, крупный заголовок SB Sans Display;
- финальная карточка = информационный слайд: светлый фон, надстрочник
  капсом, заголовок, до 4 «стеклянных» карточек 2×2 (белые 70%, тень,
  градиентный заголовок #1AB3B0 → #51B8EE → #A3B5F3), робот справа,
  логотип внизу справа.

Ассеты — в brand/ рядом с файлом (divider_bg.png, info_bg.png, logo.png,
robot.png). Нет ассетов — рисуется фирменный градиентный фон без картинок.

Используется из auto_edit.py; отдельно — для предпросмотра:
    python brand_cards.py edit.json  → _edit/title.png, _edit/end.png
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(HERE, "brand")
FONT_CANDIDATES = [os.path.join(HERE, "..", "Сборка HTML агента", "SBSansDisplay-Regular.ttf"),
                   r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

TEXT, BODY, EYEBROW = (13, 13, 13), (89, 89, 89), (74, 168, 218)
GRAD = [(0.0, (0x1A, 0xB3, 0xB0)), (0.47, (0x51, 0xB8, 0xEE)), (0.74, (0xA3, 0xB5, 0xF3)), (1.0, (0xA3, 0xB5, 0xF3))]


def font(path, px):
    return ImageFont.truetype(path, px)


def find_font(custom=None):
    for p in ([custom] if custom else []) + FONT_CANDIDATES:
        if p and os.path.exists(p):
            return p
    raise SystemExit("brand_cards: не найден шрифт")


def asset(name):
    p = os.path.join(BRAND, name)
    return Image.open(p).convert("RGBA") if os.path.exists(p) else None


def cover(img, W, H):
    """Масштаб с обрезкой под W×H (как background-size: cover)."""
    k = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def fallback_bg(W, H):
    """Фирменный светлый градиент: мятный слева снизу → голубой → лавандовый справа снизу."""
    small = Image.new("RGB", (64, 36))
    px = small.load()
    for y in range(36):
        for x in range(64):
            u, v = x / 63, y / 35
            r = int(240 + 10 * (1 - u) - 14 * u * v)
            g = int(248 - 6 * u * v)
            b = int(250 + 4 * u - 2 * (1 - u) * v)
            px[x, y] = (min(r, 255), min(g, 255), min(b, 255))
    return small.resize((W, H), Image.BICUBIC).convert("RGBA")


def gradient_text(size, text, fnt):
    """Текст с градиентом 45° (#1AB3B0 → #51B8EE → #A3B5F3)."""
    l, t, r, b = fnt.getbbox(text)
    w, h = r - l + 4, b - t + 4
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((-l + 2, -t + 2), text, font=fnt, fill=255)
    grad = Image.new("RGBA", (w, h))
    gp = grad.load()
    for y in range(h):
        for x in range(w):
            p = (x / max(w, 1) * 0.7 + y / max(h, 1) * 0.3)
            for (p0, c0), (p1, c1) in zip(GRAD, GRAD[1:]):
                if p0 <= p <= p1:
                    k = (p - p0) / (p1 - p0) if p1 > p0 else 0
                    gp[x, y] = tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)) + (255,)
                    break
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out, t


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def glass_card(base, box, radius, s):
    """Карточка: тень 15%, заливка белым 70%, тонкая светлая рамка."""
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 - int(4 * s), y0 + int(10 * s), x1 - int(4 * s), y1 + int(10 * s)),
                                             radius, fill=(17, 21, 27, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(40 * s)))
    base.alpha_composite(shadow)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius, fill=(255, 255, 255, 178), outline=(255, 255, 255, 230), width=max(1, int(1.5 * s)))
    base.alpha_composite(layer)


def paste_logo(img, logo, x, y, w):
    if logo is None:
        return
    h = round(logo.height * w / logo.width)
    img.alpha_composite(logo.resize((w, h), Image.LANCZOS), (x, y))


def render_title(cfg, W, H, font_path, out):
    """Титульная карточка — слайд-разделитель."""
    s = W / 1920
    bg = asset("divider_bg.png")
    # в шаблоне фон растянут на весь слайд (не обрезан) — так же
    img = bg.resize((W, H), Image.LANCZOS) if bg else fallback_bg(W, H)
    d = ImageDraw.Draw(img)
    paste_logo(img, asset("logo.png"), int(0.042 * W), int(0.102 * H), int(0.137 * W))
    f_t = font(font_path, int(96 * s))
    f_s = font(font_path, int(40 * s))
    x, maxw = int(0.042 * W), int(0.62 * W)
    lines = wrap(d, cfg["text"], f_t, maxw)
    y = int(0.47 * H) - (len(lines) - 1) * int(56 * s)
    for ln in lines:
        d.text((x, y), ln, font=f_t, fill=TEXT)
        y += int(112 * s)
    if cfg.get("subtitle"):
        for ln in wrap(d, cfg["subtitle"], f_s, maxw):
            d.text((x, y + int(14 * s)), ln, font=f_s, fill=BODY)
            y += int(54 * s)
    img.convert("RGB").save(out)


def end_cards(cfg):
    """cards: [{title, text}] или lines: ['30 операций — разнесены по статьям', …]."""
    if cfg.get("cards"):
        return [(c.get("title", ""), c.get("text", "")) for c in cfg["cards"]][:4]
    out = []
    for line in cfg.get("lines", [])[:4]:
        head, sep, rest = line.partition(" — ")
        out.append((head, rest) if sep else (line, ""))
    return out


def render_end(cfg, W, H, font_path, out):
    """Финальная карточка — информационный слайд."""
    s = W / 1920
    bg = asset("info_bg.png")
    img = cover(bg, W, H) if bg else fallback_bg(W, H)
    d = ImageDraw.Draw(img)
    x0 = int(0.042 * W)
    # надстрочник и заголовок
    eb = cfg.get("eyebrow", "РЕЗУЛЬТАТ")
    f_e = font(font_path, int(22 * s))
    ex = x0
    for ch in eb:
        d.text((ex, int(0.026 * H)), ch, font=f_e, fill=EYEBROW)
        ex += d.textlength(ch, font=f_e) + int(3 * s)
    d.text((x0 - int(4 * s), int(0.070 * H)), cfg.get("title", "Результат"), font=font(font_path, int(64 * s)), fill=TEXT)

    robot = asset("robot.png")
    cards = end_cards(cfg)
    right = 0.648 if robot else 0.958
    gap = int(0.019 * W)
    cols = 2 if len(cards) > 1 else 1
    rows = (len(cards) + cols - 1) // cols
    cw = int(((right - 0.042) * W - gap * (cols - 1)) / cols)
    top, bottom = int(0.30 * H), int(0.93 * H)
    ch = int(min(0.30 * H, (bottom - top - gap * (rows - 1)) / max(rows, 1)))
    f_h, f_b = font(font_path, int(56 * s)), font(font_path, int(36 * s))
    for k, (head, body) in enumerate(cards):
        r, c = divmod(k, cols)
        bx, by = x0 + c * (cw + gap), top + r * (ch + gap)
        glass_card(img, (bx, by, bx + cw, by + ch), int(min(cw, ch) * 0.085), s)
        d = ImageDraw.Draw(img)
        pad = int(0.019 * W)
        ty = by + int(pad * 0.9)
        for ln in wrap(d, head, f_h, cw - 2 * pad)[:2]:
            g, _ = gradient_text(img.size, ln, f_h)
            img.alpha_composite(g, (bx + pad, ty))
            ty += int(66 * s)
        ty += int(10 * s)
        for ln in wrap(d, body, f_b, cw - 2 * pad)[:3]:
            d.text((bx + pad, ty), ln, font=f_b, fill=BODY)
            ty += int(46 * s)
    if robot:
        rh = int(0.697 * H)
        rw = round(robot.width * rh / robot.height)
        img.alpha_composite(robot.resize((rw, rh), Image.LANCZOS), (int(0.648 * W) + (int(0.343 * W) - rw) // 2, int(0.246 * H)))
    if cfg.get("note"):
        d = ImageDraw.Draw(img)
        d.text((x0, int(0.955 * H)), cfg["note"], font=font(font_path, int(22 * s)), fill=BODY)
    paste_logo(img, asset("logo.png"), int(0.917 * W), int(0.960 * H), int(0.069 * W))
    img.convert("RGB").save(out)


def main():
    cfg_path = os.path.abspath(sys.argv[1])
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    W, H = cfg.get("size", [1920, 1080])
    work = os.path.join(os.path.dirname(cfg_path), "_edit")
    os.makedirs(work, exist_ok=True)
    fp = find_font(cfg.get("font"))
    if cfg.get("title"):
        render_title(cfg["title"], W, H, fp, os.path.join(work, "title.png"))
    if cfg.get("end"):
        render_end(cfg["end"], W, H, fp, os.path.join(work, "end.png"))
    print("OK:", work)


if __name__ == "__main__":
    main()
