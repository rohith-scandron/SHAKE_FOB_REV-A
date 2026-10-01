# HUAWEI Band 6 keychain case

A keychain frame for the HUAWEI Band 6: the four sides only, no strap mounts, flat ends
and a keyring loop. The screen and the heart-rate sensor stay uncovered.

| File | |
|---|---|
| `band6_keychain_case.step` | CAD (STEP) |
| `band6_keychain_case.stl` | ready to slice |
| `band6_keychain_case.py` | CadQuery source, all sizes at the top |
| `preview.png` | renders |

Outside size: **27.4 × 56.7 × 9.4 mm** (including the loop).

## Fit

The fit geometry was measured from the proven Band 6 frame
[thing:6260208](https://www.thingiverse.com/thing:6260208) and rebuilt as a clean solid.
The rebuild matches the reference surface to a median deviation of 0.003 mm.
- 25.38 × 42.6 mm cavity with 1.0 mm side walls and the same curved screen-side edge
- button opening in the same spot
- the two internal tongues that clip into the watch's own strap slots. These are what
  hold the watch in the frame, so they are kept.

What changed: the 22 mm spring-bar ears are removed, the ends are closed flat, the outer
corners are rounded, and a round keyring eye is added. The eye has a wide triangular base
so the pull goes into the solid end corners.

The loop is on the end that hangs at the bottom when you look at the screen with the button
on the left (`RING_END = -1`; set it to `1` to swap ends). It is a round eye (9 mm outside,
4.6 mm hole) set close to the case, so it sticks out only 7.2 mm past the case end.

## Printing

- Print with the flat back face on the bed. It needs no supports: the tongue pockets are
  short bridges.
- Material: PETG or PLA (the reference was printed rigid), 0.4 mm nozzle, 0.12–0.16 mm
  layers, 3+ walls.
- Fitting: slide one end's tongue into the watch's strap slot, then press the other end
  in until it clicks.
- If it is too tight, set `CLEAR = 0.1` in the script and re-run
  `python3 band6_keychain_case.py`.

## License

Derived from "22mm adapter for Huawei band 6 and Honor band 6" by M7md_says_hello
(thing:6260208), licensed **CC BY-SA**. This derivative is shared under the same license.
