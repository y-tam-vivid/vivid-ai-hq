#!/usr/bin/env python3
"""
snspipe.py - イベント現場向け SNS 素材生成パイプライン

使い方:
  # ストーリー（9:16・テキスト帯付き）
  python3 snspipe.py --in /mnt/user-data/uploads --mode story \
      --badge "NOW 13:00" --headline "午後も受付中" --sub "17:00まで / 出入り自由" \
      --note "tane｜LAB  グランフロント大阪" --prefix s1300

  # カルーセル（4:5）
  python3 snspipe.py --in /mnt/user-data/uploads --mode carousel --prefix c1300

  # リール（9:16 mp4・複数枚をKen Burnsでつなぐ）
  python3 snspipe.py --in /mnt/user-data/uploads --mode reel \
      --headline "つくる楽しさを、" --sub "すべての子どもに。" --prefix r1700

  # 座標グリッド（手動ぼかし領域を決めるための下見）
  python3 snspipe.py --in /mnt/user-data/uploads --mode grid --prefix G

オプション:
  --noblur            自動顔ぼかしを無効化
  --band x0,y0,x1,y1  手動ぼかし領域を%指定（複数回指定可）
  --sec 3.0           リール1枚あたりの秒数
  --focus 0.5,0.45    クロップ中心（x%,y%）
  --zoom 1.0          1.0未満で寄る
  --bg / --accent     ブランドカラー（HEX）

注意: 自動顔検出は横顔・小さい顔・遮蔽された顔を取りこぼす。
      出力は必ず目視確認し、漏れは --band で補うこと。
"""
import argparse, glob, os, subprocess, sys
import cv2, numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance, ImageFont

NAVY = (10, 22, 48)      # 既定の背景色（--bg で上書き）
ORANGE = (255, 138, 0)   # 既定のアクセント色（--accent で上書き）
WHITE = (255, 255, 255)


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
FONT_DIR = '/usr/share/fonts/opentype/noto'


def font(weight, size):
    return ImageFont.truetype(f'{FONT_DIR}/NotoSansCJK-{weight}.ttc', size)


# ---------------- 画像処理 ----------------

def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert('RGB')


def detect_faces(im):
    """haar カスケードで顔候補を検出し、% 座標の矩形リストで返す"""
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    h, w = arr.shape[:2]
    s = 1600 / max(h, w)
    small = cv2.resize(arr, (int(w * s), int(h * s)))
    gray = cv2.equalizeHist(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
    cds = [cv2.CascadeClassifier(cv2.data.haarcascades + n) for n in
           ('haarcascade_frontalface_alt2.xml', 'haarcascade_profileface.xml')]
    boxes = []
    for c in cds:
        for (x, y, bw, bh) in c.detectMultiScale(gray, 1.08, 5, minSize=(22, 22)):
            boxes.append((x, y, bw, bh))
    flip = cv2.flip(gray, 1)
    for (x, y, bw, bh) in cds[1].detectMultiScale(flip, 1.08, 5, minSize=(22, 22)):
        boxes.append((gray.shape[1] - x - bw, y, bw, bh))
    out = []
    for (x, y, bw, bh) in boxes:  # 1.7倍に拡張して髪・輪郭まで覆う
        cx, cy = x + bw / 2, y + bh / 2
        ew, eh = bw * 0.85, bh * 0.85
        out.append((100 * (cx - ew) / small.shape[1], 100 * (cy - eh) / small.shape[0],
                    100 * (cx + ew) / small.shape[1], 100 * (cy + eh) / small.shape[0]))
    return out


def soft_blur(im, regions):
    """% 指定領域に羽根付きのソフトぼかし（被写界深度風）"""
    base = im.copy()
    W, H = im.size
    for (x0, y0, x1, y1) in regions:
        box = (int(W * x0 / 100), int(H * y0 / 100), int(W * x1 / 100), int(H * y1 / 100))
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        rad = max(14, int(max(box[2] - box[0], box[3] - box[1]) * 0.30))
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).rectangle(box, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(max(6, (box[2] - box[0]) // 8)))
        base = Image.composite(base.filter(ImageFilter.GaussianBlur(rad)), base, mask)
    return base


def grade(im):
    im = ImageEnhance.Brightness(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.10)
    im = ImageEnhance.Color(im).enhance(1.12)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))


def crop(im, out_w, out_h, zoom=1.0, cx=0.5, cy=0.5):
    W, H = im.size
    ar = out_w / out_h
    if W / H > ar:
        ch = H * zoom; cw = ch * ar
    else:
        cw = W * zoom; ch = cw / ar
    if cw > W: cw = W; ch = cw / ar
    if ch > H: ch = H; cw = ch * ar
    l = min(max(W * cx - cw / 2, 0), W - cw)
    t = min(max(H * cy - ch / 2, 0), H - ch)
    return im.crop((int(l), int(t), int(l + cw), int(t + ch))).resize((out_w, out_h), Image.LANCZOS)


def prepare(path, a):
    im = load(path)
    regions = [] if a.noblur else detect_faces(im)
    for b in (a.band or []):
        regions.append(tuple(float(v) for v in b.split(',')))
    if regions:
        im = soft_blur(im, regions)
    return grade(im), len(regions)


# ---------------- テキスト合成 ----------------

def scrim(im, strength=232):
    W, H = im.size
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(H):
        if y > H * 0.52:
            aa = int(strength * ((y - H * 0.52) / (H * 0.48)) ** 1.2)
        elif y < H * 0.22:
            aa = int(140 * (1 - y / (H * 0.22)))
        else:
            aa = 0
        d.line([(0, y), (W, y)], fill=NAVY + (aa,))
    return Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')


def story_text(im, badge, headline, sub, note):
    W, H = im.size
    im = scrim(im)
    d = ImageDraw.Draw(im)
    if badge:
        f = font('Black', 44)
        w = d.textlength(badge, font=f)
        d.rectangle([70, 150, 70 + w + 44, 150 + 72], fill=ORANGE)
        d.text((92, 163), badge, font=f, fill=(12, 18, 36))
    y = H - 660
    for ln in (headline or '').split('\n'):
        d.text((70, y), ln, font=font('Black', 86), fill=WHITE)
        y += 116
    d.rectangle([70, y + 40, 200, y + 48], fill=ORANGE)
    if sub:
        d.text((70, y + 92), sub, font=font('Black', 52), fill=ORANGE)
    if note:
        d.text((70, y + 176), note, font=font('Medium', 40), fill=(214, 222, 238))
    return im


# ---------------- 各モード ----------------

def run_carousel(files, a):
    outs = []
    for i, f in enumerate(files, 1):
        im, n = prepare(f, a)
        c = crop(im, 1080, 1350, zoom=a.zoom, cx=a.fx, cy=a.fy)
        p = f'{a.out}/{a.prefix}_{i:02d}.jpg'
        c.save(p, quality=94, subsampling=0)
        outs.append(p); print(f'  {os.path.basename(f)} -> {os.path.basename(p)} (blur:{n})')
    return outs


def run_story(files, a):
    outs = []
    for i, f in enumerate(files, 1):
        im, n = prepare(f, a)
        s = crop(im, 1080, 1920, zoom=a.zoom, cx=a.fx, cy=a.fy)
        s = story_text(s, a.badge, a.headline, a.sub, a.note)
        p = f'{a.out}/{a.prefix}_{i:02d}.jpg'
        s.save(p, quality=94, subsampling=0)
        outs.append(p); print(f'  {os.path.basename(f)} -> {os.path.basename(p)} (blur:{n})')
    return outs


def run_reel(files, a):
    FPS, W, H = 30, 1080, 1920
    ns, nx = int(FPS * a.sec), int(FPS * 0.5)
    tmp = '/tmp/_reel'; os.makedirs(tmp, exist_ok=True)
    for old in glob.glob(f'{tmp}/*.jpg'):
        os.remove(old)
    frames = []
    for f in files:
        im, n = prepare(f, a)
        src = crop(im, int(W * 1.35), int(H * 1.35), zoom=a.zoom, cx=a.fx, cy=a.fy)
        sw, sh = src.size
        for i in range(ns):
            t = i / max(1, ns - 1)
            z = 1.0 - 0.10 * t
            cw, ch = sw * z / 1.35, sh * z / 1.35
            l, tp = (sw - cw) / 2, (sh - ch) * (0.35 + 0.30 * t)
            frames.append(src.crop((int(l), int(tp), int(l + cw), int(tp + ch))).resize((W, H), Image.LANCZOS))
        print(f'  {os.path.basename(f)} (blur:{n})')
    if a.headline:  # エンドカード
        end = Image.new('RGB', (W, H), NAVY)
        d = ImageDraw.Draw(end)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=(10 + 14 * y // H, 22 + 24 * y // H, 48 + 36 * y // H))
        yy = H // 2 - 190
        for ln in a.headline.split('\n'):
            d.text((84, yy), ln, font=font('Black', 96), fill=WHITE); yy += 120
        d.rectangle([84, yy + 40, 224, yy + 48], fill=ORANGE)
        if a.sub:
            d.text((84, yy + 96), a.sub, font=font('Medium', 40), fill=(210, 220, 238))
        if a.note:
            d.text((84, H - 260), a.note, font=font('Medium', 40), fill=ORANGE)
        frames += [end] * int(FPS * 2.2)
    for k in range(1, len(files) + 1):  # クロスフェード
        b = ns * k
        if b + nx < len(frames):
            for j in range(nx):
                frames[b + j] = Image.blend(frames[b - 1], frames[b + j], (j + 1) / nx)
    for i, fr in enumerate(frames):
        fr.save(f'{tmp}/f{i:04d}.jpg', quality=92)
    p = f'{a.out}/{a.prefix}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS),
                    '-i', f'{tmp}/f%04d.jpg', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '20', '-movflags', '+faststart', p], check=True)
    print(f'  -> {os.path.basename(p)}  {len(frames)/FPS:.1f}s')
    return [p]


def run_grid(files, a):
    """% 座標グリッドを重ねた縮小画像を出力。手動ぼかし領域(--band)の指定に使う"""
    outs = []
    for i, f in enumerate(files, 1):
        im = load(f)
        W, H = im.size
        s = 1100 / max(W, H)
        g = im.resize((int(W * s), int(H * s)))
        d = ImageDraw.Draw(g)
        w2, h2 = g.size
        fnt = font('Regular', 22)
        for k in range(11):
            x = int(w2 * k / 10); d.line([(x, 0), (x, h2)], fill=(255, 0, 0))
            d.text((x + 3, 3), str(k * 10), font=fnt, fill=(255, 255, 0))
            y = int(h2 * k / 10); d.line([(0, y), (w2, y)], fill=(255, 0, 0))
            d.text((3, y + 3), str(k * 10), font=fnt, fill=(0, 255, 255))
        p = f'{a.out}/{a.prefix}_grid_{i:02d}.jpg'
        g.save(p, quality=88); outs.append(p)
        print(f'  {os.path.basename(f)} -> {os.path.basename(p)}  ({W}x{H})')
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--mode', choices=['carousel', 'story', 'reel', 'grid'], required=True)
    ap.add_argument('--out', default='/mnt/user-data/outputs')
    ap.add_argument('--prefix', default='post')
    ap.add_argument('--badge', default=''); ap.add_argument('--headline', default='')
    ap.add_argument('--sub', default=''); ap.add_argument('--note', default='')
    ap.add_argument('--sec', type=float, default=3.0)
    ap.add_argument('--zoom', type=float, default=1.0)
    ap.add_argument('--focus', default='0.5,0.45')
    ap.add_argument('--noblur', action='store_true')
    ap.add_argument('--band', action='append')
    ap.add_argument('--bg', default='#0A1630', help='背景/スクリム色 HEX')
    ap.add_argument('--accent', default='#FF8A00', help='アクセント色 HEX')
    a = ap.parse_args()
    global NAVY, ORANGE
    NAVY, ORANGE = hex2rgb(a.bg), hex2rgb(a.accent)
    a.fx, a.fy = (float(v) for v in a.focus.split(','))
    # シェル経由で渡された "\n" を改行として扱う
    for k in ('headline', 'sub', 'note', 'badge'):
        setattr(a, k, getattr(a, k).replace('\\n', '\n'))
    os.makedirs(a.out, exist_ok=True)

    files = []
    for pat in a.inp.split(','):
        files += sorted(glob.glob(f'{pat}/*.*') if os.path.isdir(pat) else glob.glob(pat))
    files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.webp'))]
    if not files:
        sys.exit('画像が見つかりません: ' + a.inp)
    print(f'{len(files)}枚を処理 / mode={a.mode}')
    {'carousel': run_carousel, 'story': run_story,
     'reel': run_reel, 'grid': run_grid}[a.mode](files, a)
    print('完了')


if __name__ == '__main__':
    main()
