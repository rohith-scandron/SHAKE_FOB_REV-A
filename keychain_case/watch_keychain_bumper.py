"""Keychain bumper for the HUAWEI Band 6 (open front + back).

A frame that wraps only the 4 sides of the watch, with a small lip at the top
and bottom edge so the watch snaps in flush and can't fall out. The screen
and the heart-rate sensor stay uncovered. A ring on one side holds the keyring.

Body size is Huawei's official spec: 43 x 25.4 x 10.99 mm. Corner radius and
button position are estimates -- print the fit-test ring first (see README).
Run:  python3 watch_keychain_bumper.py
"""
import cadquery as cq

# ---- HUAWEI Band 6 body, straps removed (official spec) -----------------
WATCH_W = 25.4        # left-right width
WATCH_H = 43.0        # top-bottom length (strap direction)
WATCH_T = 10.99       # thickness, glass to back
WATCH_R = 6.5         # corner radius seen from the front (estimate)

# ---- Fit / frame ---------------------------------------------------------
CLEAR = 0.15          # gap per side (TPU: 0.1-0.15, PETG/PLA: 0.2)
WALL = 1.8            # side wall thickness
LIP = 1.0             # how far the front/back lips overhang the watch edge
LIP_T = 1.0           # thickness of each lip

# ---- Keyring loop --------------------------------------------------------
RING_OD = 9.0         # outer diameter of the loop
RING_ID = 5.0         # hole for the split ring
RING_T = 3.5          # loop thickness (centered on the frame)

# ---- Side button cut-out (right side). Set BTN_LEN = 0 to disable. -------
BTN_LEN = 12.0        # length of the opening along the side (generous)
BTN_OFFSET = 0.0      # shift of the opening from center (+ = toward top)

# -------------------------------------------------------------------------
iw, ih = WATCH_W + 2 * CLEAR, WATCH_H + 2 * CLEAR
ir = WATCH_R + CLEAR
ow, oh, orad = iw + 2 * WALL, ih + 2 * WALL, ir + WALL
total_t = WATCH_T + 2 * CLEAR + 2 * LIP_T


def rrect(w, h, r, t):
    return (cq.Workplane("XY").sketch().rect(w, h).vertices().fillet(r)
            .finalize().extrude(t))


# outer shell
body = rrect(ow, oh, orad, total_t).translate((0, 0, -total_t / 2))

# pocket for the watch (full inner size, between the lips)
pocket = rrect(iw, ih, ir, WATCH_T + 2 * CLEAR).translate(
    (0, 0, -(WATCH_T + 2 * CLEAR) / 2))
# front + back windows (smaller than the watch by LIP on each side)
wr = max(ir - LIP, 0.5)
window = rrect(iw - 2 * LIP, ih - 2 * LIP, wr, total_t + 2).translate(
    (0, 0, -total_t / 2 - 1))
frame = body.cut(pocket).cut(window)

# soften outer edges
frame = frame.faces(">Z or <Z").edges().fillet(0.4)

# side button opening on the right wall
if BTN_LEN > 0:
    btn = (cq.Workplane("XY").box(WALL * 3, BTN_LEN, WATCH_T * 0.6)
           .translate((ow / 2, BTN_OFFSET, 0)))
    frame = frame.cut(btn)

# keyring loop on the top edge (where a strap would attach)
ring_c = oh / 2 + RING_OD / 2 - 0.8          # slight overlap with the wall
tab_y0 = oh / 2 - WALL / 2                    # tab starts inside the wall
loop = (cq.Workplane("XY").circle(RING_OD / 2).extrude(RING_T)
        .translate((0, ring_c, 0))
        .union(cq.Workplane("XY").center(0, (tab_y0 + ring_c) / 2)
               .rect(RING_OD, ring_c - tab_y0).extrude(RING_T))
        .translate((0, 0, -RING_T / 2)))
hole = (cq.Workplane("XY").circle(RING_ID / 2).extrude(RING_T + 2)
        .translate((0, ring_c, -RING_T / 2 - 1)))
frame = frame.union(loop.cut(pocket)).cut(hole)

if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    cq.exporters.export(frame, os.path.join(here, "watch_keychain_bumper.step"))
    cq.exporters.export(frame, os.path.join(here, "watch_keychain_bumper.stl"),
                        tolerance=0.02, angularTolerance=0.1)
    # fit-test ring: a 3 mm slice of the side wall only (no lips, no loop).
    # Print it first (~5 min) and slide it over the watch to check the fit.
    ring = rrect(ow, oh, orad, 3).cut(rrect(iw, ih, ir, 3))
    cq.exporters.export(ring, os.path.join(here, "fit_test_ring.stl"),
                        tolerance=0.02, angularTolerance=0.1)
    bb = frame.val().BoundingBox()
    print(f"outer size: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
