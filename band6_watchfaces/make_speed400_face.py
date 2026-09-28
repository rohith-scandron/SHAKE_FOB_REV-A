"""Speed 400 -- rider's-eye view of a Triumph Speed 400 heading into a sunset. HUAWEI Band 6, 10 fps.

Top: sunset road rushing toward you (lane dashes, pine trees streaming past).
Bottom: the cockpit -- handlebar with grips, levers and bar-end mirrors (showing the dusk sky behind), the
glossy Phantom Black tank, and the round speedo whose
needle floats around 90-100 km/h; the time and date sit in the speedo's LCD like on the real bike.
Budget: the road is one moving region (10 unique frames), the needle a small one (5 unique frames).
Output: ./speed400/Speed400.hwt (+ preview.gif)
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.expanduser('~/.claude/skills/band6-watchface/scripts'))
from facekit import INK, SS, S, build_face, capsule, ell, finish, poly, thick_path  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speed400')
N, MS = 10, 100
AGENCY = r'C:/Windows/Fonts/AGENCYB.TTF'
BAHN = r'C:/Windows/Fonts/bahnschrift.ttf'

HY, SB, VPX = 104, 236, 97          # horizon, road bottom (z = 1), vanishing point x
ROAD_HALF = 150                     # road half-width at z = 1
TREE_H, TREE_OFF = 90, 34
C = (97, 272)                       # speedo centre
LCD = (72, 286, 122, 320)

TANK = (16, 16, 22)                 # Phantom Black
CHROME = (176, 180, 192)
BAR = (22, 22, 26)
DASH = (246, 226, 170)
TREE = (30, 16, 40)


def zy(z):
    return HY + (SB - HY) / z


def gradient(stops, h):
    """Vertical colour ramp: stops = [(y, (r, g, b)), ...] in screen px -> array (S(h), 3)."""
    ys = np.arange(S(h)) / SS
    out = np.zeros((len(ys), 3))
    for c in range(3):
        out[:, c] = np.interp(ys, [y for y, _ in stops], [col[c] for _, col in stops])
    return out



def background():
    sky = gradient([(0, (18, 10, 40)), (40, (52, 22, 76)), (78, (160, 52, 96)), (98, (250, 128, 64)),
                    (HY, (255, 176, 90)), (368, (255, 176, 90))], 368)
    img = Image.fromarray(np.repeat(sky[:, None, :], S(194), axis=1).astype(np.uint8), 'RGB').convert('RGBA')
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, a in ((60, 30), (44, 50), (34, 80)):
        ell(gd, VPX, 100, r, r, (255, 200, 120, a))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    ell(d, VPX, 100, 25, 25, (255, 222, 140))                    # sun
    rnd = random.Random(4)
    for _ in range(16):                                           # first stars
        ell(d, rnd.uniform(4, 190), rnd.uniform(4, 44), 0.6, 0.6, (200, 190, 230))
    for bx, by, s in ((40, 58, 1.0), (52, 52, 0.8), (150, 62, 0.9)):   # birds
        d.line([S(bx - 5 * s), S(by - 2 * s), S(bx), S(by + 1), S(bx + 5 * s), S(by - 2 * s)], fill=(40, 16, 50),
               width=S(1.2), joint='curve')
    far = [(0, 94), (18, 86), (34, 92), (52, 80), (70, 90), (86, 84), (104, 92), (124, 78), (146, 90), (164, 83),
           (182, 91), (194, 87), (194, HY), (0, HY)]
    poly(d, far, (120, 44, 96))
    near = [(0, 98), (26, 94), (48, 100), (60, HY), (134, HY), (150, 98), (172, 93), (194, 97), (194, HY + 1), (0, HY + 1)]
    poly(d, near, (66, 26, 70))
    # fields and road
    poly(d, [(0, HY), (194, HY), (194, 368), (0, 368)], (40, 24, 50))
    road = [(VPX - 2, HY), (VPX + 2, HY), (VPX + ROAD_HALF, SB), (VPX - ROAD_HALF, SB)]
    poly(d, road, (48, 42, 60))
    shade = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    poly(sd, [(VPX - 1, HY), (VPX + 1, HY), (VPX + 14, HY + 30), (VPX - 14, HY + 30)], (255, 170, 90, 40))  # sun glare
    img.alpha_composite(shade)
    d = ImageDraw.Draw(img)
    for side in (-1, 1):                                           # edge lines
        pts = [(VPX + side * (ROAD_HALF - 8) / z, zy(z)) for z in (40, 1)]
        d.line([S(pts[0][0]), S(pts[0][1]), S(pts[1][0]), S(pts[1][1])], fill=(200, 180, 190), width=S(1.4))
    return img


def tree(d, x, yb, h):
    w = 0.42 * h
    thick_path(d, [(x, yb), (x, yb - h * 0.2)], max(1.0, h * 0.06), (24, 12, 30))
    for k, (f0, f1) in enumerate(((0.12, 0.62), (0.38, 0.84), (0.62, 1.0))):
        ww = w * (1 - 0.28 * k)
        poly(d, [(x - ww / 2, yb - h * f0), (x + ww / 2, yb - h * f0), (x, yb - h * f1)], TREE)


def scene(d, t):
    """Moving parts: lane dashes and roadside trees, advanced by t in [0, 1)."""
    for k in range(1, 40):                                         # dashes every 0.5 in z
        z0 = 0.5 * k - t
        if z0 < 0.4:
            continue
        z1 = z0 + 0.22
        pts = [(VPX - 2.4 / z0, zy(z0)), (VPX + 2.4 / z0, zy(z0)), (VPX + 2.4 / z1, zy(z1)), (VPX - 2.4 / z1, zy(z1))]
        poly(d, pts, DASH)
    items = []
    for k in range(1, 16):
        items.append((k - t, -1))
        items.append((k + 0.5 - t, 1))
    for z, side in sorted(items, key=lambda it: -it[0]):          # far first
        if z < 0.6:
            continue
        tree(d, VPX + side * (ROAD_HALF + TREE_OFF) / z, zy(z), TREE_H / z)


def cockpit(d, img):
    # Phantom Black tank: glossy black catching the dusk sky and the sunset ahead
    ell(d, 97, 424, 122, 118, INK)
    ell(d, 97, 424, 120, 116, TANK)
    hi = Image.new('RGBA', img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.arc([S(-6), S(320), S(200), S(528)], 205, 335, fill=(120, 60, 140, 110), width=S(10))   # sky sheen
    hd.arc([S(-22), S(309), S(216), S(539)], 222, 318, fill=(255, 150, 80, 190), width=S(2.4))  # sunset rim
    hd.line([S(46), S(338), S(58), S(330), S(70), S(326)], fill=(255, 255, 255, 170), width=S(2), joint='curve')
    img.alpha_composite(hi)
    d = ImageDraw.Draw(img)
    ell(d, 97, 352, 11, 9, INK)                                    # fuel cap
    ell(d, 97, 352, 9.5, 7.5, CHROME)
    ell(d, 95, 350, 4, 3, (230, 232, 240))
    # handlebar sweeping down to the grips at the screen edges, levers over the grips
    bar = [(2, 273), (18, 264), (52, 250), (97, 240), (142, 250), (176, 264), (192, 273)]
    capsule(d, bar, 9, BAR, ow=2)
    for sx in (-1, 1):
        inner, outer = (97 - sx * 67, 258), (97 - sx * 91, 271)
        capsule(d, [inner, outer], 15, (36, 36, 40), ow=2)
        for k in range(4):
            x = inner[0] + (outer[0] - inner[0]) * (0.2 + 0.2 * k)
            y = inner[1] + (outer[1] - inner[1]) * (0.2 + 0.2 * k)
            d.line([S(x), S(y - 6), S(x), S(y + 6)], fill=(60, 60, 66), width=S(1))
        lever = bezier_pts((97 - sx * 64, 251), (97 - sx * 78, 242), (97 - sx * 96, 247))
        capsule(d, lever, 3.4, CHROME, ow=1.3)
    # bar-end mirrors: round, hanging off the bar ends, showing the darker eastern sky behind the rider
    for sx in (-1, 1):
        mx, my = 97 - sx * 89, 298
        capsule(d, [(97 - sx * 94, 272), (mx, my - 12)], 5, BAR, ow=1.4)
        ell(d, mx, my, 18, 15, INK)
        ell(d, mx, my, 16.5, 13.5, (34, 34, 40))
        glass = gradient([(my - 12, (16, 14, 44)), (my + 1, (58, 44, 98)), (my + 12, (34, 30, 56))], 368)
        gimg = Image.fromarray(np.repeat(glass[:, None, :], S(194), axis=1).astype(np.uint8), 'RGB').convert('RGBA')
        m = Image.new('L', img.size, 0)
        ell(ImageDraw.Draw(m), mx, my, 14, 11.5, 255)
        img.paste(gimg, (0, 0), m)
        d = ImageDraw.Draw(img)
        poly(d, [(mx - 1.5, my + 2), (mx + 1.5, my + 2), (mx + 9, my + 11), (mx - 9, my + 11)], (46, 40, 58))  # road
        if sx == -1:                                               # moon rising behind you (right mirror)
            ell(d, mx - 6, my - 5, 2.6, 2.6, (232, 228, 208))
        ell(d, mx + 5, my - 8, 0.6, 0.6, (200, 196, 230))
        d.line([S(mx - 10), S(my - 3), S(mx - 5), S(my - 8)], fill=(255, 255, 255), width=S(1.2))   # glint
    return d


def bezier_pts(p0, p1, p2, steps=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]) for t in (k / steps for k in range(steps + 1))]


def ang(v):
    return math.radians(210 - 1.2 * v)          # 0 km/h at lower left, 200 at lower right, 240 deg sweep


def speedo(img, v):
    d = ImageDraw.Draw(img)
    cx, cy = C
    ell(d, cx, cy, 65, 65, INK)                                    # chrome bezel
    ell(d, cx, cy, 63, 63, (200, 204, 214))
    ell(d, cx, cy, 60, 60, (120, 124, 136))
    ell(d, cx, cy, 57.5, 57.5, (40, 40, 46))
    ell(d, cx, cy, 55.5, 55.5, (12, 12, 16))
    d.arc([S(cx - 54), S(cy - 54), S(cx + 54), S(cy + 54)], 0, 360, fill=(70, 70, 80), width=S(0.8))
    f = ImageFont.truetype(AGENCY, S(11))
    for v0 in range(0, 201, 10):
        a = ang(v0)
        major = v0 % 20 == 0
        r1, r2 = 52, (44.5 if major else 47.5)
        d.line([S(cx + r1 * math.cos(a)), S(cy - r1 * math.sin(a)), S(cx + r2 * math.cos(a)), S(cy - r2 * math.sin(a))],
               fill=(245, 245, 250) if major else (140, 140, 150), width=S(1.7 if major else 1.0))
        if v0 % 40 == 0 and v0 < 200:                             # 200 would hit the LCD
            d.text((S(cx + 37 * math.cos(a)), S(cy - 37 * math.sin(a))), str(v0), font=f, fill=(240, 240, 245),
                   anchor='mm')
    # LCD (the time/date layers are drawn into it by the band)
    d.rounded_rectangle([S(LCD[0] - 1), S(LCD[1] - 1), S(LCD[2] + 1), S(LCD[3] + 1)], radius=S(6), fill=(70, 80, 90))
    d.rounded_rectangle([S(LCD[0]), S(LCD[1]), S(LCD[2]), S(LCD[3])], radius=S(5), fill=(8, 18, 24))
    # needle + hub
    a = ang(v)
    tip = (cx + 46 * math.cos(a), cy - 46 * math.sin(a))
    n = (-math.sin(a), -math.cos(a))
    poly(d, [(cx + 2.4 * n[0], cy + 2.4 * n[1]), tip, (cx - 2.4 * n[0], cy - 2.4 * n[1])], (236, 48, 36))
    ell(d, cx, cy, 7.5, 7.5, INK)
    ell(d, cx, cy, 6.2, 6.2, (70, 72, 80))
    ell(d, cx - 1.5, cy - 1.5, 2.4, 2.4, (170, 172, 184))
    gl = Image.new('RGBA', img.size, (0, 0, 0, 0))                  # glass reflection
    ImageDraw.Draw(gl).arc([S(cx - 50), S(cy - 50), S(cx + 50), S(cy + 50)], 120, 200, fill=(255, 255, 255, 36),
                           width=S(6))
    img.alpha_composite(gl)


def main():
    bg = background()
    frames = []
    for f in range(N):
        img = bg.copy()
        scene(ImageDraw.Draw(img), f / N)
        cockpit(ImageDraw.Draw(img), img)
        speedo(img, 95 + 6 * math.sin(2 * math.pi * f / N))
        frames.append(finish(img))
    lcd_cx = (LCD[0] + LCD[2]) // 2
    build_face('Speed400', frames, OUT, interval_ms=MS, title_cn='\u901f\u5ea6400', brief='Speed 400 sunset ride',
               clock=dict(y=LCD[1] + 3, cx=lcd_cx, size=17, height=18, color=(205, 235, 255), font=BAHN,
                          variation='SemiBold', colon_w=5),
               date=dict(y=LCD[1] + 22, cx=lcd_cx, size=11, height=11, color=(140, 196, 226), font=BAHN,
                         variation='SemiBold', gap=3))


if __name__ == '__main__':
    main()
