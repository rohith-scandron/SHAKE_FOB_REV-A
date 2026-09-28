"""Scuba cat -- cartoon of the "scuba dance" meme kitten (brown-grey tabby head, white face, pinkish-white body
with grey patches), HUAWEI Band 6, 10 fps, on black like the GIF.

Dance as in the Tenor GIF: sways side to side with the head tilting; one paw on the nose while the other swings
out, switching through a centre pose with both paws at the mouth and a little dip.
Memory trick: the whole kitten moves, so every unique pose costs ~60 KB of the 790 KB PSRAM. The dance is 5 poses
played left -> right -> left (0 1 2 3 4 4 3 2 1 0 at 100 ms = 1 s), plus one blink per 3 s loop.
Output: ./scubacat/ScubaCat.hwt (+ preview.gif, preview_sheet.png)
"""
import os
import sys

from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.expanduser('~/.claude/skills/band6-watchface/scripts'))
from facekit import INK, S, build_face, canvas, capsule, egg, ell, finish, poly, thick_path  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scubacat')
MS = 100
DANCE = [0, 1, 2, 3, 4, 4, 3, 2, 1, 0]            # lean left -> right -> left; 1 s, repeated 3x = 30 frames
BLINK = {19, 20}                                   # pose-0 frames with closed eyes (200 ms blink every 3 s)

TABBY = (122, 106, 98)
TABBY_D = (72, 60, 56)
WHITE = (246, 238, 234)
PINKISH = (236, 218, 214)
PATCH = (138, 128, 126)
SHADE = (206, 194, 190)
PINK = (238, 150, 160)
EYE = (26, 20, 18)
IRIS = (70, 52, 36)


def paw(d, x, y, r):
    ell(d, x, y, r + 2.2, r * 0.9 + 2.0, INK)
    ell(d, x, y, r, r * 0.9, WHITE)
    for k in (-1, 0, 1):
        thick_path(d, [(x + k * r * 0.36, y - r * 0.15), (x + k * r * 0.36, y + r * 0.4)], 1.1, SHADE)


def draw_head(eyes):
    img = Image.new('RGBA', (S(194), S(368)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for sx in (-1, 1):                                               # big kitten ears
        poly(d, [(97 + sx * 14, 132), (97 + sx * 56, 96), (97 + sx * 52, 154)], INK)
        poly(d, [(97 + sx * 17, 131), (97 + sx * 53, 101), (97 + sx * 50, 151)], TABBY)
        poly(d, [(97 + sx * 24, 132), (97 + sx * 48, 110), (97 + sx * 46, 146)], PINK)
    poly(d, egg(97, 170, 54.5, 48.5, taper=0.12), INK)
    poly(d, egg(97, 170, 52, 46, taper=0.12), TABBY)
    poly(d, [(89, 124), (105, 124), (108, 150), (130, 174), (132, 196), (97, 214), (62, 196), (64, 174), (86, 150)],
         WHITE)                                                      # white blaze + lower face
    for x0, y0, x1, y1 in ((80, 128, 84, 142), (114, 128, 110, 142), (60, 146, 72, 152), (134, 146, 122, 152),
                           (97, 118, 97, 126)):
        thick_path(d, [(x0, y0), (x1, y1)], 3, TABBY_D)             # tabby stripes
    for ex in (76, 118):
        if eyes == 'closed':
            d.arc([S(ex - 9), S(162), S(ex + 9), S(176)], 200, 340, fill=EYE, width=S(2.8))
        else:
            ell(d, ex, 170, 10, 11, IRIS)
            ell(d, ex, 170.5, 8.2, 9.2, EYE)
            ell(d, ex - 3, 166, 3.2, 3.2, (255, 255, 255))
            ell(d, ex + 3, 174, 1.5, 1.5, (255, 255, 255))
    poly(d, [(92, 184), (102, 184), (97, 190)], PINK)
    for sx in (-1, 1):                                               # whiskers
        for dy, ang in ((-2, -5), (3, 0), (8, 5)):
            d.line([S(97 + sx * 24), S(194 + dy), S(97 + sx * 48), S(194 + dy + ang)], fill=SHADE, width=S(1.1))
    return img


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _arm(d, sh, target, side):
    """Shoulder -> elbow (bent outward and down) -> paw."""
    mid = _lerp(sh, target, 0.5)
    elbow = (mid[0] + side * 14, mid[1] + 10)
    capsule(d, [sh, elbow, target], 16.5, PINKISH, ow=2.2)
    ell(d, elbow[0], elbow[1] - 2, 6.5, 7.5, PATCH)
    paw(d, target[0], target[1], 12)


def draw_kitten(pose, eyes='open'):
    """pose 0 = lean left (left paw out, right paw on the nose), 2 = centre (both paws at the mouth, dip),
    4 = lean right (right paw out, left paw on the nose); 1 and 3 are in between."""
    s = (pose - 2) / 2                             # -1 .. 1
    dip = 8 * (1 - abs(s))                         # bounce down through the centre pose
    img = Image.new('RGBA', (S(194), S(368)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # bow-legged stance: feet planted wide, knees push out on the dip
    for sx in (-1, 1):
        hip = (97 + sx * 20, 282 + dip)
        knee = (97 + sx * (36 + 0.6 * dip), 298 + dip * 0.45)
        foot = (97 + sx * 38, 322)
        capsule(d, [hip, knee, foot], 21, PINKISH, ow=2.2)
        ell(d, knee[0], knee[1] - 4, 8, 9, PATCH)
        ell(d, foot[0] + sx * 4, foot[1] + 2, 15.2, 9.2, INK)
        ell(d, foot[0] + sx * 4, foot[1] + 2, 13, 7, WHITE)
    # upper body on its own layer: leans around the hips
    up = Image.new('RGBA', img.size, (0, 0, 0, 0))
    u = ImageDraw.Draw(up)
    poly(u, egg(97, 250, 42.5, 48.5, taper=-0.12), INK)
    poly(u, egg(97, 250, 40, 46, taper=-0.12), PINKISH)
    ell(u, 97, 246, 24, 34, WHITE)
    ell(u, 76, 268, 10, 14, PATCH)                                   # grey belly patches
    ell(u, 120, 258, 8, 11, PATCH)
    up.alpha_composite(draw_head(eyes).rotate(-8 * s, resample=Image.BICUBIC, center=(S(97), S(214))))
    u = ImageDraw.Draw(up)
    chin_l, chin_r, nose = (86, 204), (109, 202), (97, 186)
    out_l, out_r = (38, 186), (156, 186)
    left = _lerp(chin_l, out_l, -s) if s <= 0 else _lerp(chin_l, nose, s)
    right = _lerp(chin_r, out_r, s) if s >= 0 else _lerp(chin_r, nose, -s)
    arms = [((72, 222), left, -1), ((122, 222), right, 1)]
    if s > 0:                                      # the paw on the nose is drawn in front
        arms.reverse()
    for sh, target, side in arms:
        _arm(u, sh, target, side)
    img.alpha_composite(up.rotate(-5 * s, resample=Image.BICUBIC, center=(S(97), S(292)), translate=(0, S(dip))))
    return img


def main():
    bg = canvas((0, 0, 0))
    cats, frames = {}, []
    for f in range(30):
        key = (DANCE[f % 10], 'closed' if f in BLINK else 'open')
        if key not in cats:
            cats[key] = draw_kitten(*key)
        img = bg.copy()
        img.alpha_composite(cats[key])
        frames.append(finish(img))
    build_face('ScubaCat', frames, OUT, interval_ms=MS, title_cn='潜水猫',
               brief='Scuba dance kitten')


if __name__ == '__main__':
    main()
