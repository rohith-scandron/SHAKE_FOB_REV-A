"""Cartoon spider-hero hanging upside-down from the clock -- HUAWEI Band 6 (194 x 368) watch face.

Outputs in ./spidey/:
  SpideyHang.hwt   sways, waves and blinks at 1 fps (Second Low flip-book -- the method CatBlink proved works)
  SpideyFast.hwt   waves and blinks at 10 fps with an ordered_res animation layer. ThemeStudio does not offer
                   that layer for Band 6, so this one is an experiment.
  preview_hang.gif, preview_fast.gif, previews at the real speed
"""
import math
import os
import random
import shutil
import sys
import zipfile

from PIL import Image, ImageChops, ImageDraw

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.expanduser('~/.claude/skills/band6-watchface/scripts'))  # hwt_build lives in the skill
import hwt_build
from make_cat_face import (SS, H, W, S, _runs, bezier, clock_layout, ell, make_digits, paste_time, poly,
                           save_bmp565, thick_path)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spidey')
MAX_PATCH = 200

RED = (214, 32, 44)
RED_D = (120, 12, 22)
BLUE = (36, 80, 200)
BLUE_D = (22, 46, 128)
INK = (18, 10, 18)
EYE_W = (244, 246, 252)
THREAD = (225, 225, 235)

ANCHOR = (97, 42)            # thread starts just under the clock
SPRITE_W, SPRITE_H = 194, 250
SPRITE_Y = 100               # screen y of the (flipped) sprite's top edge

# 1 fps script: (sway degrees, waving-arm angle, eyes)
HANG = [(5 * math.sin(2 * math.pi * k / 10), a, e) for k, (a, e) in enumerate(
    [(140, 'open'), (140, 'open'), (100, 'open'), (55, 'happy'), (75, 'happy'),
     (50, 'happy'), (70, 'open'), (110, 'open'), (140, 'closed'), (140, 'open')])]
# 10 fps script (experimental ordered_res): 20 frames at 100 ms -> two waves and one blink every 2 s
FAST_MS = 100
FAST = [(0.0, 70 + 22 * math.sin(2 * math.pi * f / 10),
         {12: 'half', 13: 'closed', 14: 'half'}.get(f, 'open')) for f in range(20)]


# ---------------------------------------------------------------- drawing helpers (supersampled)
def capsule(d, pts, width, fill, outline=INK, ow=2.2):
    thick_path(d, pts, width + 2 * ow, outline)
    thick_path(d, pts, width, fill)


def egg(cx, cy, rx, ry, taper=0.12, n=96):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(t) * (1 - taper * max(0.0, math.sin(t))), cy + ry * math.sin(t)))
    return pts


def eye_shape(cx, cy, mirror, open_k=1.0, grow=1.0, n=80):
    """Classic mask eye: rounded outer side, point toward the nose, slanted."""
    rx, ry = 16 * grow, 12.5 * grow * open_k
    tip = math.radians(30)
    slant = math.radians(16)          # inner (nose) side lower, outer side higher
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        bump = 1 + 0.3 * max(0.0, math.cos(t - tip)) ** 6
        x, y = rx * math.cos(t) * bump, ry * math.sin(t) * bump
        x, y = x * math.cos(slant) - y * math.sin(slant), x * math.sin(slant) + y * math.cos(slant)
        pts.append((cx + (-x if mirror else x), cy + y))
    return pts


def draw_head(img, eyes):
    d = ImageDraw.Draw(img)
    cx, cy = 97, 62
    head = egg(cx, cy, 52, 57)
    poly(d, egg(cx, cy, 54.5, 59.5), INK)
    poly(d, head, RED)
    # web lines, clipped to the head
    web = Image.new('RGBA', img.size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(web)
    c = (97, 68)
    dirs = [2 * math.pi * k / 14 + 0.1 for k in range(14)]
    for a in dirs:
        wd.line([S(c[0]), S(c[1]), S(c[0] + 80 * math.cos(a)), S(c[1] + 80 * math.sin(a))], fill=RED_D, width=S(1.1))
    for r in (13, 25, 38, 52, 66):
        for a0, a1 in zip(dirs, dirs[1:] + dirs[:1]):
            p0 = (c[0] + r * math.cos(a0), c[1] + r * math.sin(a0))
            p1 = (c[0] + r * math.cos(a1), c[1] + r * math.sin(a1))
            am = (a0 + a1) / 2 if a1 > a0 else (a0 + a1 + 2 * math.pi) / 2
            mid = (c[0] + 0.86 * r * math.cos(am), c[1] + 0.86 * r * math.sin(am))
            pts = bezier(p0, mid, p1, steps=8)
            wd.line([(S(x), S(y)) for x, y in pts], fill=RED_D, width=S(1.1))
    mask = Image.new('L', img.size, 0)
    poly(ImageDraw.Draw(mask), head, 255)
    img.paste(web, (0, 0), ImageChops.multiply(mask, web.getchannel('A')))
    d = ImageDraw.Draw(img)
    for ex, mirror in ((71, False), (123, True)):
        k = {'open': 1.0, 'half': 0.45, 'happy': 0.5, 'closed': 0.12}[eyes]
        ey = 60 - (4 if eyes == 'happy' else 0)
        poly(d, eye_shape(ex, ey, mirror, max(k, 0.3), grow=1.3), INK)
        if eyes != 'closed':
            poly(d, eye_shape(ex, ey + (3 if eyes == 'happy' else 0), mirror, k), EYE_W)
    return img


def draw_emblem(d, cx, cy):
    ell(d, cx, cy + 4, 3.6, 6.5, INK)
    ell(d, cx, cy - 4, 2.6, 2.6, INK)
    for side in (-1, 1):
        for k, (ax, ay, bx, by) in enumerate(((5, -4, 8, -12), (6, -1, 11, -6), (6, 3, 11, 9), (5, 6, 8, 14))):
            thick_path(d, [(cx + side * 1.5, cy + k * 2 - 2), (cx + side * ax, cy + ay), (cx + side * bx, cy + by)], 1.3, INK)


def draw_arm(d, shoulder, alpha, side):
    a = math.radians(alpha)
    bend = math.radians(14) * side
    elbow = (shoulder[0] + side * 24 * math.sin(a), shoulder[1] + 24 * math.cos(a))
    hand = (elbow[0] + side * 24 * math.sin(a - bend * side), elbow[1] + 24 * math.cos(a - bend * side))
    capsule(d, [shoulder, elbow], 15, BLUE)
    capsule(d, [elbow, hand], 14, RED)
    ell(d, hand[0], hand[1], 11.2, 11.2, INK)
    ell(d, hand[0], hand[1], 9, 9, RED)


def draw_sprite(wave_alpha, eyes):
    """Upright hero on a transparent sprite canvas; the caller flips it upside-down."""
    img = Image.new('RGBA', (S(SPRITE_W), S(SPRITE_H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in (86, 108):                                          # legs + boots
        capsule(d, [(x, 168), (x, 214)], 22, BLUE)
        capsule(d, [(x, 212), (x, 232)], 23, RED)
        ell(d, x, 239, 14.5, 8.5, INK)
        ell(d, x, 239, 12.5, 6.5, RED)
    poly(d, egg(97, 142, 34, 38, taper=-0.05), INK)              # torso
    poly(d, egg(97, 142, 31.5, 35.5, taper=-0.05), BLUE)
    poly(d, [(71, 112), (123, 112), (116, 150), (104, 170), (90, 170), (78, 150)], RED)
    ell(d, 97, 171, 25, 6, INK)
    ell(d, 97, 171, 23, 4.2, RED)                                # belt
    draw_emblem(d, 97, 134)
    draw_head(img, eyes)
    d = ImageDraw.Draw(img)
    draw_arm(d, (68, 122), 140, -1)                              # resting arm
    draw_arm(d, (126, 122), wave_alpha, 1)                       # waving arm
    return img


def draw_background():
    img = Image.new('RGBA', (S(W), S(H)), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(26):                                          # dim stars
        x, y = rnd.uniform(4, 190), rnd.uniform(50, 250)
        ell(d, x, y, 0.7, 0.7, (90, 90, 110))
    ell(d, 160, 84, 15, 15, (200, 196, 172))                     # crescent moon
    ell(d, 153, 79, 14, 14, (0, 0, 0))
    web = (70, 70, 84)                                           # corner web
    for k in range(6):
        a = math.radians(-2 + k * 18.4)
        d.line([S(0), S(0), S(62 * math.cos(a)), S(62 * math.sin(a))], fill=web, width=S(1))
    for r in (14, 26, 38, 50):
        pts = []
        for k in range(6):
            a = math.radians(-2 + k * 18.4)
            pts.append((r * math.cos(a), r * math.sin(a)))
        for p0, p1 in zip(pts, pts[1:]):
            mid = ((p0[0] + p1[0]) / 2 * 0.88, (p0[1] + p1[1]) / 2 * 0.88)
            d.line([(S(x), S(y)) for x, y in bezier(p0, mid, p1, 8)], fill=web, width=S(1))
    x = 0                                                        # night skyline
    while x < W:
        bw, bh = rnd.randint(14, 30), rnd.randint(26, 78)
        d.rectangle([S(x), S(H - bh), S(x + bw), S(H)], fill=(20, 24, 50))
        for wy in range(H - bh + 6, H - 4, 8):
            for wx in range(x + 4, x + bw - 3, 6):
                if rnd.random() < 0.3:
                    d.rectangle([S(wx), S(wy), S(wx + 2), S(wy + 3)], fill=(92, 84, 40))
        x += bw + rnd.randint(1, 4)
    return img


def render_frame(bg, sway, wave_alpha, eyes):
    layer = Image.new('RGBA', bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    feet_y = SPRITE_Y + SPRITE_H - 244
    d.line([S(ANCHOR[0]), S(ANCHOR[1]), S(97), S(feet_y + 2)], fill=THREAD, width=S(1.6))
    ell(d, ANCHOR[0], ANCHOR[1], 2.2, 2.2, THREAD)
    layer.alpha_composite(draw_sprite(wave_alpha, eyes).rotate(180), (0, S(SPRITE_Y)))
    if abs(sway) > 1e-6:
        layer = layer.rotate(sway, resample=Image.BICUBIC, center=(S(ANCHOR[0]), S(ANCHOR[1])))
    return Image.alpha_composite(bg, layer).resize((W, H), Image.LANCZOS).convert('RGB')


# ---------------------------------------------------------------- patches
def patch_boxes(frames, margin=3):
    """Boxes covering every changed pixel; boxes larger than 200 px are cut into equal tiles. Even sizes."""
    mask = Image.new('L', frames[0].size, 0)
    for f in frames[1:]:
        mask = ImageChops.lighter(mask, ImageChops.difference(frames[0], f).convert('L').point(lambda v: 255 if v else 0))
    px, (w, h) = mask.load(), mask.size
    rows = [any(px[x, y] for x in range(w)) for y in range(h)]
    boxes = []
    for y0, y1 in _runs(rows):
        cols = [any(px[x, y] for y in range(y0, y1 + 1)) for x in range(w)]
        for x0, x1 in _runs(cols, gap=12):
            boxes.append((max(0, x0 - margin), max(0, y0 - margin), min(w, x1 + 1 + margin), min(h, y1 + 1 + margin)))
    out = []
    for x0, y0, x1, y1 in boxes:
        nx, ny = math.ceil((x1 - x0) / MAX_PATCH), math.ceil((y1 - y0) / MAX_PATCH)
        for i in range(nx):
            for j in range(ny):
                a0, a1 = x0 + (x1 - x0) * i // nx, x0 + (x1 - x0) * (i + 1) // nx
                b0, b1 = y0 + (y1 - y0) * j // ny, y0 + (y1 - y0) * (j + 1) // ny
                a0, b0 = a0 - a0 % 2, b0 - b0 % 2
                a1, b1 = a1 + (a1 - a0) % 2, b1 + (b1 - b0) % 2
                if a1 > w:
                    a0, a1 = a0 - 2, a1 - 2
                if b1 > h:
                    b0, b1 = b0 - 2, b1 - 2
                assert a1 - a0 <= MAX_PATCH and b1 - b0 <= MAX_PATCH
                out.append((a0, b0, a1, b1))
    return out


def export_patches(frames, boxes, folder, fmt):
    """Write every frame's crop of every box; returns [[path per frame] per box]."""
    shutil.rmtree(folder, ignore_errors=True)
    paths = []
    for k, (x0, y0, x1, y1) in enumerate(boxes):
        os.makedirs(os.path.join(folder, f'p{k}'), exist_ok=True)
        col = []
        for i, im in enumerate(frames):
            p = os.path.join(folder, f'p{k}', f'f{i:02d}.{fmt}')
            crop = im.crop((x0, y0, x1, y1))
            save_bmp565(crop, p) if fmt == 'bmp' else crop.convert('RGBA').save(p)
            col.append(p)
        paths.append(col)
    # self-check: background (frame 0) + patches rebuild every frame exactly
    for i, im in enumerate(frames):
        rebuilt = frames[0].copy()
        for x0, y0, x1, y1 in boxes:
            rebuilt.paste(im.crop((x0, y0, x1, y1)), (x0, y0))
        assert rebuilt.tobytes() == im.tobytes(), f'frame {i} not rebuilt'
    return paths


def clock_layers(digits, lay):
    dig = lambda n: os.path.join(digits, f'{n}.png')
    return [dict(draw='selected_res', res=[dig(n) for n in range(3)], pos=lay['Hour High'], value_type=59),
            dict(draw='selected_res', res=[dig(n) for n in range(10)], pos=lay['Hour Low'], value_type=60),
            dict(draw='single_res', res=dig('colon'), pos=lay['colon']),
            dict(draw='selected_res', res=[dig(n) for n in range(6)], pos=lay['Minute High'], value_type=61),
            dict(draw='selected_res', res=[dig(n) for n in range(10)], pos=lay['Minute Low'], value_type=62)]


def build(name, title_cn, brief, frames, digits, lay, animated):
    folder = os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    boxes = patch_boxes(frames)
    fmt = 'png' if animated else 'bmp'   # opaque 16-bit patches: half the size of RGBA PNG
    patches = export_patches(frames, boxes, os.path.join(folder, 'patches'), fmt)
    bg = os.path.join(folder, 'background.bmp')
    save_bmp565(frames[0], bg)
    thumb = os.path.join(folder, 'res.bmp')
    save_bmp565(paste_time(frames[0].copy(), digits, lay).resize((126, 238), Image.LANCZOS), thumb)
    if animated:
        moving = [dict(draw='ordered_res', res=col, pos=box[:2], interval=FAST_MS, mode='loop')
                  for col, box in zip(patches, boxes)]
    else:
        moving = [dict(draw='selected_res', res=col, pos=box[:2], value_type=64) for col, box in zip(patches, boxes)]
    # ordered layers go after the clock (animated layers are indexed after normal ones anyway)
    time_layers = (clock_layers(digits, lay) + moving) if animated else (moving + clock_layers(digits, lay))
    spec = dict(title_en=name, title_cn=title_cn, author='Rohith', brief=brief, thumbnail=thumb,
                elements=[('background', [dict(draw='single_res', res=bg, pos=(0, 0))]), ('time', time_layers)])
    hwt = os.path.join(OUT, name + '.hwt')
    info = hwt_build.build_face(spec, hwt)
    # self-check: decode the compiled face and compare with the intended frames (565 rounding only)
    b = zipfile.ZipFile(hwt).read('com.huawei.watchface')
    for i, im in enumerate(frames):
        got = (hwt_build.render(b, 10, 8, 0, t_ms=i * FAST_MS) if animated else hwt_build.render(b, 10, 8, i)).tobytes()
        want = paste_time(im.copy(), digits, lay, '1008').convert('RGB').tobytes()
        assert max(abs(p - q) for p, q in zip(got, want)) <= 8, f'{name}: frame {i} renders wrong'
    print(f'{hwt}: version {info["version"]}, {os.path.getsize(hwt)} bytes, {info["resources"]} images, '
          f'{len(boxes)} moving layer(s) {[(x1 - x0, y1 - y0) for x0, y0, x1, y1 in boxes]}, render check OK')
    for nm, val, lim in info['checks']:
        print(f'  {nm}: {val} / {lim}')
    return b


def main():
    os.makedirs(OUT, exist_ok=True)
    digits = os.path.join(OUT, 'digits')
    cw, colw, _ = make_digits(digits)
    lay = clock_layout(cw, colw)
    bg = draw_background()

    hang = [render_frame(bg, *spec) for spec in HANG]
    fast = [render_frame(bg, *spec) for spec in FAST]
    build('SpideyHang', '倒挂蜘蛛侠', 'Spider hero hanging from the clock', hang, digits, lay, False)
    build('SpideyFast', '快蜘蛛侠', 'Spider hero waving fast', fast, digits, lay, True)

    for name, frames, ms in (('preview_hang.gif', hang, 1000), ('preview_fast.gif', fast, FAST_MS)):
        seq = [paste_time(f.copy(), digits, lay) for f in frames]
        seq[0].save(os.path.join(OUT, name), save_all=True, append_images=seq[1:], duration=ms, loop=0)
    sheet = Image.new('RGB', (W * 3 + 16, H), (50, 50, 50))
    for k, i in enumerate((0, 3, 8)):
        sheet.paste(paste_time(hang[i].copy(), digits, lay), (k * (W + 8), 0))
    # keep only the deliverables: the two .hwt files + their preview GIFs
    for p in ('SpideyHang', 'SpideyFast', 'digits', 'preview_sheet.png'):
        p = os.path.join(OUT, p)
        shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else (os.path.exists(p) and os.remove(p))


if __name__ == '__main__':
    main()
