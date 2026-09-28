"""Original cartoon cat watch face for HUAWEI Band 6 (194x368 AMOLED), built for Theme Studio.

Band 6 (194x368) faces have no frame-animation control. They do have "Selected image", which picks one
of 10 images from a value; bound to "Second Low" (last digit of the seconds) that gives a 1 fps,
10-frame flip-book.

Outputs in ./cat_blink/:
  CatBlink.hwt            installable face, compiled by hwt_build.py (no Theme Studio needed)
  bmp/background_cat.bmp, bmp/aod_background.bmp   static cat / AOD backgrounds (16-bit R5G6B5)
  png32/patches/pK/cat_0..9.png   Second Low patches over the parts of the cat that move
  png32/digits/0..9.png, colon.png   clock digits
  res.bmp                 126x238, 16-bit R5G6B5 thumbnail (Theme Studio requires it for 194x368)
  gallery/*.png           stills for the official Gallery watch face (388x736)
  preview.gif             10 s preview at 1 fps with a sample time
  preview_sheet.png       all 10 frames
  layout.txt              exact x/y for every layer
"""
import math
import os
import shutil
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.expanduser('~/.claude/skills/band6-watchface/scripts'))  # hwt_build lives in the skill

W, H = 194, 368
TOP = 44
SS = 4
FONT = r'C:/Windows/Fonts/seguibl.ttf'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cat_blink')
# AOD layers make the face version 2.2, which Band 6 firmware without AOD support rejects
# ("Watch face is for a newer version"); plain faces are 2.1
WITH_AOD = False

FUR = (255, 168, 72)
FUR_DARK = (214, 118, 40)
CREAM = (255, 232, 196)
PINK = (255, 150, 172)
EYE = (28, 24, 30)
WHITE = (255, 255, 255)
HEART = (255, 92, 130)

# 1 fps flip-book script: (tail phase 0..1, eyes, left-ear twitch, heart progress or None)
FLIPBOOK = [
    (0.00, 'open', False, None),
    (0.10, 'open', False, None),
    (0.20, 'open', False, 0.0),
    (0.30, 'open', False, 0.35),
    (0.40, 'closed', False, 0.7),
    (0.50, 'open', False, 1.0),
    (0.60, 'open', False, None),
    (0.70, 'open', True, None),
    (0.80, 'open', False, None),
    (0.90, 'half', False, None),
]


def S(v):
    return int(round(v * SS))


def ell(d, cx, cy, rx, ry, fill):
    d.ellipse([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], fill=fill)


def poly(d, pts, fill):
    d.polygon([(S(x), S(y)) for x, y in pts], fill=fill)


def thick_path(d, pts, width, fill):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.line([S(x0), S(y0), S(x1), S(y1)], fill=fill, width=S(width))
    for x, y in pts:
        ell(d, x, y, width / 2, width / 2, fill)


def bezier(p0, p1, p2, steps=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
            for t in (k / steps for k in range(steps + 1))]


def heart(d, cx, cy, size, fill):
    r = size * 0.3
    ell(d, cx - r, cy - r * 0.4, r, r, fill)
    ell(d, cx + r, cy - r * 0.4, r, r, fill)
    poly(d, [(cx - 2 * r, cy - r * 0.1), (cx + 2 * r, cy - r * 0.1), (cx, cy + 2.1 * r)], fill)


def draw_cat(phase, eyes='open', twitch=False, heart_k=None, size=(W, H)):
    img = Image.new('RGBA', (S(W), S(H)), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    sway = 14 * math.sin(2 * math.pi * phase)
    tail = bezier((138, 318), (196, 318), (168 + sway, 238))
    thick_path(d, tail, 16, FUR)
    for t in (0.55, 0.75, 0.92):
        x, y = tail[int(t * (len(tail) - 1))]
        ell(d, x, y, 8.2, 3.2, FUR_DARK)

    ell(d, 97, 290, 60, 62, FUR)
    ell(d, 97, 300, 33, 42, CREAM)
    ell(d, 76, 343, 17, 11, CREAM)
    ell(d, 118, 343, 17, 11, CREAM)
    for x in (70, 76, 82, 112, 118, 124):
        d.line([S(x), S(339), S(x), S(346)], fill=FUR_DARK, width=S(1.2))

    tw = (-5, 4) if twitch else (0, 0)
    poly(d, [(46, 150), (57 + tw[0], 80 + tw[1]), (92, 118)], FUR)
    poly(d, [(56, 140), (61 + tw[0], 94 + tw[1]), (83, 121)], PINK)
    poly(d, [(148, 150), (137, 80), (102, 118)], FUR)
    poly(d, [(138, 140), (133, 94), (111, 121)], PINK)

    ell(d, 97, 172, 60, 55, FUR)
    for x, dy in ((85, 2), (97, 0), (109, 2)):
        thick_path(d, [(x, 121 + dy), (x, 133 + dy)], 3.2, FUR_DARK)
    ell(d, 97, 200, 28, 19, CREAM)

    blush = Image.new('RGBA', img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    ell(bd, 64, 196, 11, 7, (255, 110, 150, 120))
    ell(bd, 130, 196, 11, 7, (255, 110, 150, 120))
    img = Image.alpha_composite(img, blush)
    d = ImageDraw.Draw(img)

    for ex in (74, 120):
        if eyes == 'closed':
            d.arc([S(ex - 11), S(166), S(ex + 11), S(184)], 200, 340, fill=EYE, width=S(3.2))
        elif eyes == 'half':
            ell(d, ex, 176, 11, 7, EYE)
            ell(d, ex - 4, 174, 2.6, 2.2, WHITE)
        else:
            ell(d, ex, 172, 11, 14, EYE)
            ell(d, ex - 4, 166, 4.2, 4.2, WHITE)
            ell(d, ex + 4, 178, 2, 2, WHITE)

    poly(d, [(91, 191), (103, 191), (97, 198)], PINK)
    d.arc([S(85), S(193), S(97), S(206)], 20, 160, fill=EYE, width=S(2.2))
    d.arc([S(97), S(193), S(109), S(206)], 20, 160, fill=EYE, width=S(2.2))
    for dy, ang in ((-2, -6), (4, 0), (10, 6)):
        d.line([S(66), S(198 + dy), S(34), S(198 + dy + ang)], fill=CREAM, width=S(1.4))
        d.line([S(128), S(198 + dy), S(160), S(198 + dy + ang)], fill=CREAM, width=S(1.4))

    if heart_k is not None:
        hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
        heart(ImageDraw.Draw(hl), 158, 112 - 30 * heart_k, 16, HEART + (int(255 * (1 - heart_k * 0.8)),))
        img = Image.alpha_composite(img, hl)

    return img.resize(size, Image.LANCZOS).convert('RGB')


# ---------------------------------------------------------------- clock digits
def make_digits(folder, height=30):
    os.makedirs(folder, exist_ok=True)
    f = ImageFont.truetype(FONT, 26)
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    cw = max(int(probe.textlength(str(k), font=f)) for k in range(10)) + 2
    widths = {}
    for c in [str(k) for k in range(10)] + [':']:
        wdt = cw if c != ':' else 10
        im = Image.new('RGBA', (wdt, height), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.text(((wdt - dd.textlength(c, font=f)) / 2, 0), c, font=f, fill=WHITE + (255,))
        im.save(os.path.join(folder, ('colon' if c == ':' else c) + '.png'), optimize=True)
        widths[c] = wdt
    return cw, widths[':'], height


def clock_layout(cw, colw, y=8):
    total = 4 * cw + colw
    x0 = (W - total) // 2
    return {'Hour High': (x0, y), 'Hour Low': (x0 + cw, y), 'colon': (x0 + 2 * cw, y),
            'Minute High': (x0 + 2 * cw + colw, y), 'Minute Low': (x0 + 3 * cw + colw, y)}


def paste_time(img, digits_dir, layout, hhmm='1008'):
    for key, ch in zip(('Hour High', 'Hour Low', 'Minute High', 'Minute Low'), hhmm):
        d = Image.open(os.path.join(digits_dir, ch + '.png'))
        img.paste(d, layout[key], d)
    c = Image.open(os.path.join(digits_dir, 'colon.png'))
    img.paste(c, layout['colon'], c)
    return img


# ---------------------------------------------------------------- 16-bit R5G6B5 BMP
def save_bmp565(img, path):
    """16-bit R5G6B5 BMP with a BITMAPV4HEADER (the variant Theme Studio accepts)."""
    img = img.convert('RGB')
    w, h = img.size
    row = (w * 2 + 3) & ~3
    px = img.load()
    data = bytearray()
    for y in range(h - 1, -1, -1):
        line = bytearray()
        for x in range(w):
            r, g, b = px[x, y]
            line += struct.pack('<H', ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3))
        data += line + b'\x00' * (row - len(line))
    off = 14 + 108
    v4 = struct.pack('<IiiHHIIiiII', 108, w, h, 1, 16, 3, len(data), 2835, 2835, 0, 0)
    v4 += struct.pack('<IIII', 0xF800, 0x07E0, 0x001F, 0)
    v4 += b'BGRs' + b'\x00' * 36 + struct.pack('<III', 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(struct.pack('<2sIHHI', b'BM', off + len(data), 0, 0, off) + v4 + data)


MAX_PATCH = 200   # Theme Studio: Time-layer images must be <= 200 x 200 px

AOD_LINE = (150, 88, 36)      # dim orange outline
AOD_ZZZ = (110, 110, 140)


def draw_cat_aod(size=(W, H)):
    """Sleeping line-art cat for the always-on display: sparse, dim, no animation."""
    img = Image.new('RGB', (S(W), S(H)), (0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = S(2.2)

    def oval(cx, cy, rx, ry, a0=0, a1=360):
        d.arc([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], a0, a1, fill=AOD_LINE, width=lw)

    # curled body + tail wrapped round the front
    oval(97, 262, 64, 50)
    tail = bezier((150, 290), (120, 338), (62, 318))
    for (x0, y0), (x1, y1) in zip(tail, tail[1:]):
        d.line([S(x0), S(y0), S(x1), S(y1)], fill=AOD_LINE, width=lw)
    # head resting on the body
    oval(97, 196, 50, 44)
    d.line([S(55), S(172), S(60), S(126), S(86), S(154)], fill=AOD_LINE, width=lw, joint='curve')
    d.line([S(139), S(172), S(134), S(126), S(108), S(154)], fill=AOD_LINE, width=lw, joint='curve')
    # closed eyes, nose, mouth
    for ex in (78, 116):
        oval(ex, 196, 10, 7, 20, 160)
    d.polygon([(S(93), S(207)), (S(101), S(207)), (S(97), S(212))], outline=AOD_LINE, width=S(1.5))
    oval(91, 213, 6, 5, 20, 160)
    oval(103, 213, 6, 5, 20, 160)
    # z z z
    f = ImageFont.truetype(FONT, S(14))
    for k, (x, y) in enumerate(((140, 140), (152, 120), (164, 100))):
        f = ImageFont.truetype(FONT, S(10 + 4 * k))
        d.text((S(x), S(y)), 'z', font=f, fill=AOD_ZZZ)
    return img.resize(size, Image.LANCZOS)


def lit_ratio(img, thresh=16):
    """Fraction of non-black pixels (any channel above thresh)."""
    g = img.convert('RGB')
    n = sum(1 for p in g.getdata() if max(p) > thresh)
    return n / (g.width * g.height)


def _runs(profile, gap=6):
    """Group indices with non-zero values into runs, bridging gaps up to `gap`."""
    runs, start, last = [], None, None
    for i, v in enumerate(profile):
        if v:
            if start is None:
                start = i
            elif i - last > gap:
                runs.append((start, last))
                start = i
            last = i
    if start is not None:
        runs.append((start, last))
    return runs


def split_patches(frames, margin=3):
    """Boxes (x0, y0, x1, y1) covering every pixel that changes between frames, each <= 200 x 200, even sizes."""
    from PIL import ImageChops
    mask = Image.new('L', frames[0].size, 0)
    for f in frames[1:]:
        d = ImageChops.difference(frames[0], f).convert('L').point(lambda v: 255 if v > 0 else 0)
        mask = ImageChops.lighter(mask, d)
    px = mask.load()
    w, h = mask.size
    rows = [any(px[x, y] for x in range(w)) for y in range(h)]
    boxes = []
    for y0, y1 in _runs(rows):
        cols = [any(px[x, y] for y in range(y0, y1 + 1)) for x in range(w)]
        for x0, x1 in _runs(cols, gap=12):
            boxes.append([x0, y0, x1 + 1, y1 + 1])
    # merge boxes while the union still fits -> fewest layers to build by hand
    limit = MAX_PATCH - 2 * margin - 2
    merged = True
    while merged:
        merged = False
        for a in range(len(boxes)):
            for b in range(a + 1, len(boxes)):
                u = [min(boxes[a][0], boxes[b][0]), min(boxes[a][1], boxes[b][1]),
                     max(boxes[a][2], boxes[b][2]), max(boxes[a][3], boxes[b][3])]
                if u[2] - u[0] <= limit and u[3] - u[1] <= limit:
                    boxes[a] = u
                    del boxes[b]
                    merged = True
                    break
            if merged:
                break
    out = []
    for x0, y0, x1, y1 in boxes:
        x0, y0 = max(0, x0 - margin), max(TOP, y0 - margin)
        x1, y1 = min(w, x1 + margin), min(h, y1 + margin)
        x0 -= x0 % 2
        y0 -= y0 % 2
        if (x1 - x0) % 2:
            x1 = min(w, x1 + 1) if x1 < w else x1
            x0 -= (x1 - x0) % 2
        if (y1 - y0) % 2:
            y1 = min(h, y1 + 1) if y1 < h else y1
            y0 -= (y1 - y0) % 2
        assert x1 - x0 <= MAX_PATCH and y1 - y0 <= MAX_PATCH, (x0, y0, x1, y1)
        out.append((x0, y0, x1, y1))
    return out


def main():
    for sub in ('flipbook', 'gallery'):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    digits_dir = os.path.join(OUT, 'digits')
    cw, colw, dh = make_digits(digits_dir)
    lay = clock_layout(cw, colw)

    frames = [draw_cat(*spec) for spec in FLIPBOOK]
    sizes = []
    for i, im in enumerate(frames):
        p = os.path.join(OUT, 'flipbook', f'cat_{i}.png')
        im.crop((0, TOP, W, H)).quantize(colors=64, method=Image.Quantize.MEDIANCUT,
                                          dither=Image.Dither.NONE).save(p, optimize=True)
        sizes.append(os.path.getsize(p))
    Image.new('RGB', (W, H), (0, 0, 0)).save(os.path.join(OUT, 'background.png'))

    # clean up the old 8 fps sequence (Band 6 cannot play it)
    old = os.path.join(OUT, 'frames')
    if os.path.isdir(old):
        for f in os.listdir(old):
            os.remove(os.path.join(old, f))
        os.rmdir(old)
    for f in ('preview.gif',):
        if os.path.exists(os.path.join(OUT, f)):
            os.remove(os.path.join(OUT, f))

    prev = [paste_time(im.copy(), digits_dir, lay, '10' + f'0{i}') for i, im in enumerate(frames)]
    prev[0].save(os.path.join(OUT, 'preview.gif'), save_all=True, append_images=prev[1:],
                 duration=1000, loop=0, disposal=2)
    sheet = Image.new('RGB', (W * 5 + 4 * 6, H * 2 + 6), (40, 40, 40))
    for i, im in enumerate(prev):
        sheet.paste(im, ((i % 5) * (W + 6), (i // 5) * (H + 6)))
    sheet.save(os.path.join(OUT, 'preview_sheet.png'))

    save_bmp565(paste_time(frames[0].copy(), digits_dir, lay).resize((126, 238), Image.LANCZOS),
                os.path.join(OUT, 'res.bmp'))

    for name, spec in (('cat_hello', FLIPBOOK[0]), ('cat_heart', FLIPBOOK[3]), ('cat_happy', FLIPBOOK[4])):
        draw_cat(*spec, size=(2 * W, 2 * H)).save(os.path.join(OUT, 'gallery', name + '.png'), optimize=True)

    # Theme Studio (194x368) accepts only 16-bit R5G6B5 BMP for every image -> export BMP copies
    bdir = os.path.join(OUT, 'bmp')
    for sub in ('flipbook', 'digits'):
        os.makedirs(os.path.join(bdir, sub), exist_ok=True)
    save_bmp565(Image.new('RGB', (W, H), (0, 0, 0)), os.path.join(bdir, 'background.bmp'))
    for i, im in enumerate(frames):
        save_bmp565(im.crop((0, TOP, W, H)), os.path.join(bdir, 'flipbook', f'cat_{i}.bmp'))
    for name in [str(k) for k in range(10)] + ['colon']:
        dimg = Image.open(os.path.join(digits_dir, name + '.png'))
        flat = Image.new('RGB', dimg.size, (0, 0, 0))
        flat.paste(dimg, (0, 0), dimg)
        save_bmp565(flat, os.path.join(bdir, 'digits', name + '.bmp'))

    # Theme Studio wants 32-bit (RGBA) PNGs for layer images
    pdir = os.path.join(OUT, 'png32')
    for sub in ('flipbook', 'digits'):
        os.makedirs(os.path.join(pdir, sub), exist_ok=True)
    Image.new('RGBA', (W, H), (0, 0, 0, 255)).save(os.path.join(pdir, 'background.png'))
    for i, im in enumerate(frames):
        im.crop((0, TOP, W, H)).convert('RGBA').save(os.path.join(pdir, 'flipbook', f'cat_{i}.png'))
    for name in [str(k) for k in range(10)] + ['colon']:
        Image.open(os.path.join(digits_dir, name + '.png')).convert('RGBA').save(os.path.join(pdir, 'digits', name + '.png'))

    # Time-layer images are limited to 200 x 200 px: static cat goes into the background (BMP),
    # only the regions that change become small Second Low patches
    import shutil
    for d in (os.path.join(pdir, 'patches'), os.path.join(bdir, 'patches'),
              os.path.join(pdir, 'flipbook'), os.path.join(bdir, 'flipbook'), os.path.join(OUT, 'flipbook')):
        shutil.rmtree(d, ignore_errors=True)
    for f in (os.path.join(pdir, 'background.png'), os.path.join(OUT, 'background.png')):
        if os.path.exists(f):
            os.remove(f)
    boxes = split_patches(frames)
    save_bmp565(frames[0], os.path.join(bdir, 'background_cat.bmp'))
    for k, (x0, y0, x1, y1) in enumerate(boxes):
        for sub, ext in ((pdir, 'png'), (bdir, 'bmp')):
            os.makedirs(os.path.join(sub, 'patches', f'p{k}'), exist_ok=True)
        for i, im in enumerate(frames):
            crop = im.crop((x0, y0, x1, y1))
            crop.convert('RGBA').save(os.path.join(pdir, 'patches', f'p{k}', f'cat_{i}.png'))
            save_bmp565(crop, os.path.join(bdir, 'patches', f'p{k}', f'cat_{i}.bmp'))
    # self-check: background + patches must rebuild every frame exactly
    for i, im in enumerate(frames):
        rebuilt = frames[0].copy()
        for x0, y0, x1, y1 in boxes:
            rebuilt.paste(im.crop((x0, y0, x1, y1)), (x0, y0))
        assert rebuilt.tobytes() == im.tobytes(), f'frame {i} not rebuilt'

    # AOD (always-on) face: sparse sleeping line-art cat, background BMP; clock layers are copied over
    aod = draw_cat_aod()
    save_bmp565(aod, os.path.join(bdir, 'aod_background.bmp'))
    aod_prev = paste_time(aod.copy(), digits_dir, lay)
    aod_prev.save(os.path.join(OUT, 'aod_preview.png'))
    aod_ratio = lit_ratio(aod_prev)
    worst = 0.0
    for y in range(0, H - 200 + 1, 8):
        worst = max(worst, lit_ratio(aod_prev.crop((0, y, W, y + 200))))
    assert aod_ratio < 0.20 and worst < 0.60, (aod_ratio, worst)

    with open(os.path.join(OUT, 'layout.txt'), 'w') as f:
        f.write('Theme Studio layer positions (194 x 368, top-left origin)\n')
        f.write(f'AOD: bmp/aod_background.bmp  Background > Single image  x=0 y=0  '
                f'(lit {aod_ratio:.1%} of screen, worst 200px window {worst:.1%}; limits 20% / 60%)\n')
        f.write('bmp/background_cat.bmp    Background > Single image   x=0   y=0   (static cat)\n')
        for k, (x0, y0, x1, y1) in enumerate(boxes):
            f.write(f'patches/p{k}/cat_0..9      Time > Selected image       x={x0:<3} y={y0:<3} '
                    f'({x1 - x0} x {y1 - y0})  value type: Second Low\n')
        for key in ('Hour High', 'Hour Low', 'Minute High', 'Minute Low'):
            x, y = lay[key]
            f.write(f'digits/0..9.png           Selected image  x={x:<3} y={y}    value type: {key}\n')
        x, y = lay['colon']
        f.write(f'digits/colon.png          Single image    x={x:<3} y={y}\n')
        f.write('res.bmp                   upload as the 126 x 238 thumbnail (16-bit R5G6B5)\n')
    print(f'flipbook: 10 frames, {sum(sizes) / 1024:.1f} KB total, max {max(sizes) / 1024:.1f} KB')
    print(open(os.path.join(OUT, 'layout.txt')).read())

    # installable .hwt, compiled directly (hwt_build.py reproduces ThemeStudio's output byte-for-byte)
    import zipfile
    import hwt_build
    dig = lambda n: os.path.join(pdir, 'digits', f'{n}.png')
    clock = []
    for amb in ((0, 1) if WITH_AOD else (0,)):
        clock += [dict(draw='selected_res', res=[dig(n) for n in range(3)], pos=lay['Hour High'], value_type=59, ambient=amb),
                  dict(draw='selected_res', res=[dig(n) for n in range(10)], pos=lay['Hour Low'], value_type=60, ambient=amb),
                  dict(draw='single_res', res=dig('colon'), pos=lay['colon'], ambient=amb),
                  dict(draw='selected_res', res=[dig(n) for n in range(6)], pos=lay['Minute High'], value_type=61, ambient=amb),
                  dict(draw='selected_res', res=[dig(n) for n in range(10)], pos=lay['Minute Low'], value_type=62, ambient=amb)]
    patches = [dict(draw='selected_res', pos=(x0, y0), value_type=64,
                    res=[os.path.join(pdir, 'patches', f'p{k}', f'cat_{i}.png') for i in range(10)])
               for k, (x0, y0, x1, y1) in enumerate(boxes)]
    spec = dict(title_en='CatBlink', title_cn='眨眼猫', author='Rohith',
                brief='Cute cat that blinks every second', thumbnail=os.path.join(OUT, 'res.bmp'),
                elements=[('background', [dict(draw='single_res', res=os.path.join(bdir, 'background_cat.bmp'), pos=(0, 0))]
                           + ([dict(draw='single_res', res=os.path.join(bdir, 'aod_background.bmp'), pos=(0, 0), ambient=1)]
                              if WITH_AOD else [])),
                          ('time', patches + clock)])
    hwt = os.path.join(OUT, 'CatBlink.hwt')
    for old in ('CatBlink.hwt', 'CatBlink_AOD.hwt'):
        if os.path.exists(os.path.join(OUT, old)):
            os.remove(os.path.join(OUT, old))
    if WITH_AOD:
        hwt = os.path.join(OUT, 'CatBlink_AOD.hwt')
    info = hwt_build.build_face(spec, hwt)
    # self-check: decode the compiled face and compare with the intended frames (565 rounding only)
    b = zipfile.ZipFile(hwt).read('com.huawei.watchface')
    for i in range(10):
        got = hwt_build.render(b, 10, i, i).tobytes()
        want = prev[i].convert('RGB').tobytes()
        assert max(abs(p - q) for p, q in zip(got, want)) <= 8, f'second {i} renders wrong'
    if WITH_AOD:
        got = hwt_build.render(b, 10, 8, 0, ambient=True).tobytes()
        assert max(abs(p - q) for p, q in zip(got, aod_prev.convert('RGB').tobytes())) <= 8, 'AOD renders wrong'
    print(f'{hwt}: version {info["version"]}, {os.path.getsize(hwt)} bytes, {info["resources"]} images, '
          f'decoded render matches all 10 seconds' + (' + AOD' if WITH_AOD else ''))
    for name, val, lim in info['checks']:
        print(f'  {name}: {val} / {lim}')

    # keep only the deliverables: CatBlink.hwt + preview.gif (everything else is rebuilt on every run)
    for p in ('bmp', 'png32', 'digits', 'gallery', 'format_test', 'README.txt', 'layout.txt', 'aod_preview.png',
              'res.bmp', 'preview_sheet.png'):
        p = os.path.join(OUT, p)
        shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else (os.path.exists(p) and os.remove(p))


if __name__ == '__main__':
    main()
