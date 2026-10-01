# HUAWEI Band 6 keychain case

A keychain frame for the HUAWEI Band 6: the four sides only, no strap mounts, flat ends
and a keyring loop. The screen and the heart-rate sensor stay uncovered.

| File | |
|---|---|
| `band6_keychain_case.step` | CAD (STEP) |
| `band6_keychain_case.stl` | ready to slice |
| `band6_keychain_case.py` | CadQuery source, all sizes at the top |
| `preview.png` | renders |

Outside size: **27.4 × 56.7 × 10.2 mm** (including the loop).

## Fit

The fit geometry was measured from the proven Band 6 frame
[thing:6260208](https://www.thingiverse.com/thing:6260208) and rebuilt as a clean solid.
The rebuild matches the reference surface to a median deviation of 0.003 mm.
- 25.38 × 42.6 mm cavity with 1.0 mm side walls and the same curved screen-side edge
- button opening in the same spot
- the two internal tongues that clip into the watch's own strap slots. These are what
  hold the watch in the frame, so they are kept.

What changed: the 22 mm spring-bar ears are removed, the ends are closed flat, the four outer
corners are rounded (5 mm radius), and a round keyring eye is added. The eye has a wide triangular base
so the pull goes into the solid end corners.

With the keyring at the top and the screen facing you, the button opening is on the right
(`BTN_SIDE = 1`; `-1` moves it to the other wall, `RING_END` swaps the loop's end). It is a round eye (9 mm outside,
4.6 mm hole) set close to the case, so it sticks out only 7.2 mm past the case end.

A 0.8 mm inward ledge runs round the back edge (`LIP_W`, `LIP_T`). The watch is pushed in
from the screen side and stops on it, and it can't fall out the back. The ledge is added
under the old back face, so the watch sits at the same height and the tongues still line
up with its strap slots; the case is 0.8 mm thicker. The heart-rate sensor stays uncovered.

## Printing

- Print with the flat back face on the bed. It needs no supports: the tongue pockets are
  short bridges.
- Material: PETG or PLA (the reference was printed rigid), 0.4 mm nozzle, 0.12–0.16 mm
  layers, 3+ walls.
- Fitting: from the screen side, slide one end's tongue into the watch's strap slot, then
  press the other end in until it clicks and the watch sits on the back ledge.
- If it is too tight, set `CLEAR = 0.1` in the script and re-run
  `python3 band6_keychain_case.py`.

## License

Derived from "22mm adapter for Huawei band 6 and Honor band 6" by M7md_says_hello
(thing:6260208), licensed **CC BY-SA**. This derivative is shared under the same license.
