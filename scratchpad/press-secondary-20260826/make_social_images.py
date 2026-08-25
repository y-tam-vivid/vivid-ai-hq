# -*- coding: utf-8 -*-
"""Instagram用の1080x1080画像を作る。元画像は読むだけ。出力は scratchpad/social/ のみ。
何度流しても同じ結果になる。"""
import os
from PIL import Image, ImageDraw, ImageFont

SP = "/private/tmp/claude-501/-Users-yujimac/78fb95cb-ebdc-4f69-96dd-1bd89b727d06/scratchpad"
DL = os.path.expanduser("~/Downloads")
OUT = os.path.join(SP, "social")
os.makedirs(OUT, exist_ok=True)

FB = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"   # 太字
FR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"   # 本文
S = 1080


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def load_square(src, box):
    """box=(l,t,r,b) で切り出してから1080正方形へ。"""
    im = Image.open(src).convert("RGB")
    im = im.crop(box)
    w, h = im.size
    side = min(w, h)
    im = im.crop(((w - side) // 2, (h - side) // 2, (w - side) // 2 + side, (h - side) // 2 + side))
    return im.resize((S, S), Image.LANCZOS)


def wrap(draw, text, f, maxw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        t = cur + ch
        if draw.textlength(t, font=f) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def cover(src, box, title, sub, accent, out):
    """写真の下部に帯を敷いて見出しを載せる。"""
    im = load_square(src, box)
    BH = 470
    band = Image.new("RGBA", (S, BH), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 0, S, BH], fill=(20, 16, 14, 214))
    im = im.convert("RGBA")
    im.alpha_composite(band, (0, S - BH))
    d = ImageDraw.Draw(im)
    d.rectangle([64, S - BH + 54, 64 + 96, S - BH + 62], fill=accent)

    ft = font(FB, 62)
    y = S - BH + 104
    for ln in wrap(d, title, ft, S - 128):
        d.text((64, y), ln, font=ft, fill=(255, 255, 255))
        y += 82

    fs = font(FR, 31)
    y += 18
    for ln in sub.split("\n"):
        d.text((64, y), ln, font=fs, fill=(226, 220, 214))
        y += 46
    im.convert("RGB").save(os.path.join(OUT, out), quality=88)
    return out


def photo(src, box, caption, out):
    im = load_square(src, box).convert("RGBA")
    band = Image.new("RGBA", (S, 150), (20, 16, 14, 190))
    im.alpha_composite(band, (0, S - 150))
    d = ImageDraw.Draw(im)
    f = font(FR, 34)
    y = S - 150 + (150 - 44 * len(wrap(d, caption, f, S - 128))) // 2
    for ln in wrap(d, caption, f, S - 128):
        d.text((64, y), ln, font=f, fill=(255, 255, 255))
        y += 44
    im.convert("RGB").save(os.path.join(OUT, out), quality=88)
    return out


def card(bg, fg, accent, head, rows, foot, out):
    im = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([64, 96, 64 + 96, 104], fill=accent)
    fh = font(FB, 54)
    y = 146
    for ln in wrap(d, head, fh, S - 128):
        d.text((64, y), ln, font=fh, fill=fg)
        y += 74
    y += 46
    fn, fl = font(FB, 88), font(FR, 33)
    for num, lab in rows:
        d.text((64, y), num, font=fn, fill=accent)
        y += 108
        for ln in wrap(d, lab, fl, S - 128):
            d.text((64, y), ln, font=fl, fill=fg)
            y += 46
        y += 34
    if foot:
        ff = font(FR, 27)
        yy = S - 64 - 38 * len(foot.split("\n"))
        for ln in foot.split("\n"):
            d.text((64, yy), ln, font=ff, fill=fg)
            yy += 38
    im.save(os.path.join(OUT, out), quality=92)
    return out


def banner_square(src, bg, out):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    nw = S - 96
    nh = int(h * nw / w)
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (S, S), bg)
    canvas.paste(im, (48, (S - nh) // 2))
    canvas.save(os.path.join(OUT, out), quality=92)
    return out


made = []
# ── 01 親子向けAI体験イベント（ウォーム系） ─────────────────
WARM = (232, 104, 30)
made.append(cover(
    os.path.join(DL, "IMG_4463 2.jpeg"), (300, 0, 3800, 3000),
    "AI体験イベント、\n2会場で開催しました",
    "2026.7.25-26 グランフロント大阪 北館1F\n2026.8.15-16 イオンモール京都桂川 1階 月の広場",
    WARM, "01_1_cover.jpg"))
made.append(photo(
    os.path.join(DL, "IMG_4460 2.jpeg"), (0, 1100, 2200, 3300),
    "6つの質問に答えると、自分のアイデアが動き出す（グランフロント大阪）",
    "01_2_booth.jpg"))
made.append(photo(
    os.path.join(DL, "IMG_8196.jpeg"), (2650, 1100, 5628, 4078),
    "きょうだいで、友だち同士で。1組あたり約10分（イオンモール京都桂川）",
    "01_3_kyoto.jpg"))
made.append(photo(
    os.path.join(DL, "IMG_4467 2.jpeg"), (0, 2600, 4284, 5092),
    "2日間で会場はこの賑わいに（グランフロント大阪 北館1F）",
    "01_4_hall.jpg"))
made.append(card(
    (255, 247, 236), (58, 42, 26), WARM,
    "2日間×2会場で、\nこれだけの体験が生まれました",
    [("延べ332回", "7/25-26 グランフロント大阪でのAIコンテンツ体験回数"),
     ("100組以上", "同会場でのゲーム制作体験"),
     ("97%", "「たのしかった」と答えた割合")],
    "※ 会場内アンケート n=37（匿名）／数字は主催者集計",
    "01_5_numbers.jpg"))

# ── 02 福祉×AIウェビナー（ネイビー系） ──────────────────
NAVY = (20, 36, 63)
SKY = (79, 163, 209)
made.append(banner_square(os.path.join(SP, "img", "webinar_banner.jpg"), NAVY, "02_1_banner.jpg"))
made.append(card(
    NAVY, (255, 255, 255), SKY,
    "アナログな福祉業界を\nAIで業務改革",
    [("2026.8.22", "土曜 11:00-12:00 ／ オンライン開催・参加無料"),
     ("登壇", "ふくち。グループ 代表 田村有璽\n（同グループ 株式会社ILIFE として）"),
     ("テーマ", "AIを全く使ってこなかった僕が、\n福祉業界のゲームチェンジャーになるまで")],
    "企画・運営 AIコミュニティ RIALA",
    "02_2_credit.jpg"))

for m in made:
    p = os.path.join(OUT, m)
    print("%-20s %s バイト" % (m, os.path.getsize(p)))
