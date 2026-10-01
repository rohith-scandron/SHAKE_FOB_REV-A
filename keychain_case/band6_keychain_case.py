"""HUAWEI Band 6 keychain case (no strap mounts, flat ends, keyring loop).

Fit geometry is measured directly from the proven Band 6 frame
"22mm adapter for Huawei band 6 and Honor band 6" by M7md_says_hello
(https://www.thingiverse.com/thing:6260208, CC BY-SA): same 25.38 mm cavity,
1.0 mm side walls, curved screen-side edge, button opening, and the two
internal tongues that clip into the watch's own strap slots and hold it in.
The 22 mm spring-bar ears are removed and the ends closed flat.
This derivative is shared under the same CC BY-SA license.

Axes: X = width, Y = thickness (Y=0 is the flat wrist/back side -> print
this face down, no supports), Z = length. The fit geometry below is given
from the watch's back face, which ends up LIP_T above Y=0 (on the ledge).
Run:  python3 band6_keychain_case.py
"""
import cadquery as cq

# ---- measured from the reference (mm) ------------------------------------
CAV_W = 25.38         # inner width between side walls
CAV_L = 42.60         # inner length between end blocks
WALL = 1.00           # side wall thickness
END_L = 24.75         # half-length to the outer end face (flat ends)
TOP = [               # screen-side edge height vs |z| (flat 9.4 mid-section)
    (0.0, 9.40), (11.8, 9.40), (13.3, 9.37), (15.2, 9.24), (17.2, 8.90),
    (19.2, 8.40), (20.5, 7.95), (21.7, 7.40), (22.7, 6.85), (23.7, 6.20),
    (END_L, 5.50)]
CAV_R = 1.2           # cavity corner radius (front view)
OUT_R = 5.0           # outer corner radius (front view); keeps ~1 mm wall at the corners

# strap-slot tongue at each end: pocket under it + two small latch notches
POCKET_W = 14.70      # pocket width (|x| < 7.35)
POCKET_H = 5.30       # pocket height from the back face (tongue underside)
POCKET_D = 2.50       # pocket depth into the end block
NOTCH_X = (6.50, 8.50)
NOTCH_Y = (4.62, 6.62)
NOTCH_D = 0.50

# side button opening. BTN_SIDE = 1: +X wall, which is to the RIGHT when you
# look at the screen with the keyring at the top. -1 moves it to the other
# wall (the watch then sits rotated 180 degrees, so Z is mirrored too).
BTN_SIDE = 1
BTN_Z = (-5.00, 6.13)
BTN_Y = (1.87, 7.56)
BTN_R = 1.0

CLEAR = 0.0           # extra gap per side; reference fit is 0 (snug)

# back ledge (long sides only): an inward lip under the watch's back edge so the watch stops in
# the right place when pushed in from the screen side and can't fall out the
# back. It is added BELOW the old back face, so the watch still sits at the
# same height and the tongues still line up with its strap slots.
LIP_W = 0.8           # how far the lip sticks inward from the cavity wall
LIP_T = 0.8           # lip thickness (case gets this much thicker)

# ---- keyring loop ------------------------------------------------------------
RING_END = -1         # -1 = -Z end (opposite end to the original +Z loop)
RING_OD = 9.0         # round eye outer diameter
RING_ID = 4.6         # round hole diameter
RING_GAP = 0.4        # solid between the case end face and the hole
RING_BASE = 17.0      # gusset width at the case end (stays on the flat part between the rounded corners)
RING_T = 3.5          # loop thickness above the ledge layer

# ----------------------------------------------------------------------------
cw, cl = CAV_W + 2 * CLEAR, CAV_L + 2 * CLEAR
ow = cw + 2 * WALL


def rrect(w, l, r, h):
    """Rounded rectangle in XZ, extruded from Y=0 to Y=h."""
    return (cq.Workplane("XZ").sketch().rect(w, l).vertices().fillet(r)
            .finalize().extrude(-h))


# side profile (YZ plane: local x = world Y, local y = world Z):
# flat back, curved screen-side edge
top = [(y, -z) for z, y in reversed(TOP)] + [(y, z) for z, y in TOP[1:]]
profile = (cq.Workplane("YZ").moveTo(0, -END_L).lineTo(*top[0])
           .spline(top[1:], includeCurrent=True)
           .lineTo(0, END_L).close().extrude(ow / 2 + 1, both=True))
body = rrect(ow, 2 * END_L, OUT_R, 10).intersect(profile)

# cavity through the whole thickness
body = body.cut(rrect(cw, cl, CAV_R, 12).translate((0, -1, 0)))

for s in (1, -1):
    zin = s * cl / 2
    # pocket under the tongue (open to the back face)
    body = body.cut(cq.Workplane("XY").box(POCKET_W, POCKET_H + 1, POCKET_D)
                    .translate((0, (POCKET_H - 1) / 2, zin + s * POCKET_D / 2)))
    # latch notches on the tongue
    for sx in (1, -1):
        nx = sx * (NOTCH_X[0] + NOTCH_X[1]) / 2
        body = body.cut(cq.Workplane("XY")
                        .box(NOTCH_X[1] - NOTCH_X[0], NOTCH_Y[1] - NOTCH_Y[0],
                             NOTCH_D + 0.2)
                        .translate((nx, sum(NOTCH_Y) / 2,
                                    zin + s * (NOTCH_D - 0.2) / 2)))

# button opening in the BTN_SIDE wall
btn = (cq.Workplane("YZ").sketch()
       .rect(BTN_Y[1] - BTN_Y[0], BTN_Z[1] - BTN_Z[0]).vertices().fillet(BTN_R)
       .finalize().extrude(3 * WALL, both=True)
       .translate((BTN_SIDE * (cw / 2 + WALL / 2), sum(BTN_Y) / 2,
                   BTN_SIDE * sum(BTN_Z) / 2)))
body = body.cut(btn)

# back ledge, from Y=-LIP_T to 0: the case footprint under the walls, plus a
# lip LIP_W wide on the two long sides only. The short ends (top and bottom)
# have no lip, so the watch can be tilted in end first past the tongues.
lip = rrect(ow, 2 * END_L, OUT_R, LIP_T).cut(
    rrect(cw, cl, CAV_R, LIP_T + 2).translate((0, -1, 0)))
for sx in (1, -1):
    lip = lip.union(cq.Workplane("XY")
                    .box(LIP_W + WALL, LIP_T, cl - 2 * CAV_R)
                    .translate((sx * (cw / 2 - LIP_W + (LIP_W + WALL) / 2),
                                LIP_T / 2, 0)))
body = body.union(lip.translate((0, -LIP_T, 0)))

# keyring loop on the RING_END end, flush with the back face: a round eye
# pulled in close to the case so it sticks out only RING_GAP + RING_ID +
# (RING_OD - RING_ID) / 2 past the end face. Its base is a wide gusset so
# the pull goes into the solid end-block corners, not only the thin plate
# in front of the tongue pocket.
rc = END_L + RING_GAP + RING_ID / 2
loop = (cq.Workplane("XZ").center(0, rc).circle(RING_OD / 2).extrude(-RING_T)
        .union(cq.Workplane("XZ")
               .polyline([(-RING_BASE / 2, END_L - 0.5), (RING_BASE / 2, END_L - 0.5),
                          (RING_OD / 2, rc), (-RING_OD / 2, rc)]).close()
               .extrude(-RING_T)))
loop = loop.cut(cq.Workplane("XZ").center(0, rc).circle(RING_ID / 2)
                .extrude(-RING_T - 2).translate((0, -1, 0)))
loop = loop.cut(rrect(cw, cl + 2 * POCKET_D, CAV_R, 12).translate((0, -1, 0)))
if RING_END < 0:
    loop = loop.mirror("XY")
loop = loop.union(loop.faces("<Y").wires().toPending().extrude(LIP_T))
# shift up so the new back face (bottom of the ledge) is Y=0 again
case = body.union(loop).translate((0, LIP_T, 0))

if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    cq.exporters.export(case, os.path.join(here, "band6_keychain_case.step"))
    cq.exporters.export(case, os.path.join(here, "band6_keychain_case.stl"),
                        tolerance=0.01, angularTolerance=0.1)
    bb = case.val().BoundingBox()
    print(f"valid={case.val().isValid()}  size X{bb.xlen:.2f} Y{bb.ylen:.2f} "
          f"Z{bb.zlen:.2f}  bbox Z[{bb.zmin:.2f},{bb.zmax:.2f}] "
          f"Y[{bb.ymin:.2f},{bb.ymax:.2f}]")
