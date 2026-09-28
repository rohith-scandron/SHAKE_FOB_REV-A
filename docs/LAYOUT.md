# Layout guide — SHAKE_FOB_REV-A

Ref-des match the actual schematic. Rules are sourced from Espressif's
ESP32-C3 hardware design guidelines §1.4 and the Johanson 2450AT18A100E
datasheet (p.3), both in `datasheets/`.

---

## 0. Before placing anything

| Step | What |
|---|---|
| 1 | **Add C20 (1µF, C52923) + C21 (10nF, C15195) on VDDA pins 31/32** in the schematic, then press F8 (Update PCB from Schematic). The PCB currently has 48 footprints; the schematic has 55, going to 57. |
| 2 | Stackup: **2 layers, 1.6mm** (the cheap default, kept on purpose for a hobby board). |
| 3 | **Shrink the existing 3.3V zone on F.Cu.** It currently covers the whole board. Redraw it as a bounded region (see Zones below), because a board-wide 3.3V pour puts 3.3V copper right against the RF trace, the crystal and the antenna. |
| 4 | Zones: **GND on both layers** plus the bounded 3.3V region on top. B.Cu is the ground plane, so keep it as unbroken as possible. |
| 5 | **Change R1, R2 (5.1k) and R6 (1k) from 0201 to 0402**, see the box below. |
| 6 | Enter the Board Setup values in section 0a. |

> **Why 0201 has to go.** JLC **Economic PCBA** (the cheap one) only
> places parts down to **0402**. A single 0201 forces **Standard PCBA**,
> which needs a board ≥70×70mm or a panel with edge rails, plus fiducials
> and a higher setup fee. Every other part on this board is already 0402 or
> larger.
> - R1, R2 → 5.1kΩ 0402 **C25905** (Basic)
> - R6 → 1kΩ 0402 **C11702** (Basic)
>
> For the footprint, reuse any R0402 footprint already in your lib (e.g.
> `lcsc_footprints:C25531_R0402`). The land pattern is identical.
>
> Economic PCBA also means: one side only (already the plan), 0.8–1.6mm
> thick, board ≥10×10mm, and **no fiducials or edge rails needed**.

---

## 0a. Board Setup values (JLC 2-layer, 1oz, 1.6mm)

JLC limits below are from jlcpcb.com/capabilities (checked 2026-09-23).
The chosen value leaves margin over the absolute minimum, because
running at the limit is where yield drops.

### Design Rules → Constraints

| Setting | JLC min | **Use** |
|---|---|---|
| Minimum clearance | 0.10 | **0.15** |
| Minimum track width | 0.10 | **0.15** |
| Minimum connection width | — | **0.15** |
| Minimum annular width (via) | 0.05 | **0.10** |
| Minimum via diameter | 0.25 | **0.50** |
| Copper to hole clearance | 0.20 (via hole → track) | **0.20** |
| Copper to edge clearance | 0.20 (routed edge) | **0.30** |
| Minimum through hole | 0.15 | **0.30** (0.3mm drill is JLC's no-extra-cost size) |
| Hole to hole clearance | 0.20 (via), 0.45 (pad holes) | **0.25** |
| Silk: min text height / thickness | 1.0 / 0.15 | **1.0 / 0.15** |
| Silk to pad (mask) clearance | 0.15 | **0.15** |

### Design Rules → Solder Mask/Paste

| Setting | **Use** | Why |
|---|---|---|
| Solder mask expansion | **0** | JLC plots your mask 1:1 |
| Solder mask min web width | **0.10** | JLC min mask bridge, green |
| Tent vias | **on, both sides** | JLC fills tented vias with mask, so no shorts under parts |

With a 0.5mm pitch QFN/LGA, the pad gaps are ~0.2–0.25mm, above the 0.1mm
bridge, so mask dams stay between pins.

### Pre-defined Sizes — 3 widths, 1 via

| Tracks | Via (dia / drill) |
|---|---|
| **0.2** signals · **0.4** power · **0.6** RF trace only | **0.6 / 0.3** everywhere, including the EP grid |

### Net Classes — just 2

| Class | Track | Clearance | Via | Nets |
|---|---|---|---|---|
| **Default** | 0.2 | 0.15 | 0.6 / 0.3 | everything not listed below |
| **Power** | 0.4 | 0.2 | 0.6 / 0.3 | `VBUS`, `BAT`, `V_SYS`, `3.3V`, `GND` |

- **0.2mm fits everywhere,** including the QFN and LGA pads (~0.25mm wide),
  so no neck-downs are needed. USB D+/D− and the crystal lines are just
  Default, routed carefully by hand.
- **0.4mm for power** handles ~1A on 1oz outer copper. The biggest current
  here is ~200mA.
- **RF is drawn by hand at 0.6mm.** It's one ~4mm trace, so it doesn't need
  its own class. With the 0.2mm zone gap it comes out at ~63Ω. That's fine
  at this length (a true 50Ω line would be ~1.2mm wide).
- **By hand, no DRC rule:** no vias on the RF trace or the crystal lines.

### Zones (fills)

| Zone | Layer | Area | Priority |
|---|---|---|---|
| **GND** | B.Cu | whole board | 0 |
| **GND** | F.Cu | whole board | 0 |
| **3.3V** | F.Cu | **bounded region only**, see below | 1 (higher) |

Settings for all zones: clearance **0.2**, min width **0.2**, thermal
reliefs (spoke 0.3, gap 0.2), remove islands **always**. For U3, C14 and
C15, set zone connection to **Solid** in the footprint properties.

**3.3V fill: allowed, but fence it in.** Draw the 3.3V zone outline only
around the LDO → C9 → ESP32 power-pin area. Keep it **off**:
- the antenna corner, the RF trace and C14/L3/C15
- the crystal and C12/C13
- the USB D+/D− pair

Those areas need **top-layer GND** next to them: the RF trace uses the top
GND as its side walls, and the crystal needs a clean ground ring. The
whole-board top GND zone automatically fills everything the 3.3V zone
doesn't cover, because the higher-priority zone wins where they overlap.
The bottom layer stays 100% GND, which is Espressif's 2-layer rule.

### Antenna keepout

Rule area 6.5 × 6.5mm at the antenna corner, **F.Cu + B.Cu**. Tick keep out
*tracks*, *vias*, *copper pours*. **Untick** *pads* and *footprints*, so
AE1 itself can sit inside it.

### Vias in the QFN EP

9 vias, **0.6 / 0.3**, 3×3 grid at ~1.1mm pitch inside the 3.7mm EP. These
can't be tented because they're in a pad. A little solder wicks down them,
which is normal and harmless on a ground/thermal pad.

**2-layer rules (Espressif §1.4.1–1.4.2, two-layer design):**
- **B.Cu = ground.** Don't place parts on the bottom and keep traces there
  to a minimum. Any bottom trace must be short, and **never under the chip,
  the crystal, the RF trace or the antenna feed.** A long bottom trace cuts
  the ground plane and the return current has to detour around it.
- **Route power on the top layer**, including the 3V3 branches to each
  chip pin. Use vias to the bottom only when there's no other way.
- Put GND vias everywhere between top-layer pour and bottom plane: at every
  cap's GND pad, around the RF trace, around the crystal, and along the
  board edges.

**RF trace width on 2-layer:** a true 50Ω coplanar trace on 1.6mm FR4 is
~1.2mm wide with the 0.2mm zone gap (calculated for εr 4.4–4.6). A 0.6mm
trace is ~63Ω. At 2.44GHz the wavelength in this line is ~76mm, so a trace
under ~4mm (λ/20) is electrically too short for 63Ω vs 50Ω to matter.
**Decision: route it at 0.6mm and keep it short** by putting U3 right next
to the antenna corner. If the RF trace can't be kept short, make it
1.0mm wide instead.

---

## 1. Floorplan — decide the stack first

The 0.96" OLED module is ~27×28mm, so the fob is at least that size anyway.
The PCB can be the same width at no size cost.

**The one hard mechanical rule:** the antenna corner must **not** sit
behind the OLED module or the LiPo pouch. Both are large ground/metal
sheets and will detune it. Let the antenna corner stick out ~7mm beyond the
display/battery stack.

```
 ┌───────────────────────────┐
 │ (O)            ┌─────────┐│  ← 6.5×6.5mm corner: NO copper on ANY layer
 │ keyring        │   AE1   ││     antenna long axis along the board edge,
 │ hole           └────▲────┘│     feed pin 1 toward the ground plane
 │                     │ π   │  ← C15 / L3 / C14 right at U3 pin 1
 │   X1 ◄2mm+  ┌─────┐─┘     │
 │             │ U3  │   U4  │
 │   C20/C21   └─────┘       │
 │  OLED pads: GND VCC SCL SDA (2.54mm pitch)
 │  U2  Q1 D2   U1  LED1     │
 │ SW1 SW2   BAT+ BAT−   D1  │
 │          [ USB-C ]        │
 └───────────────────────────┘
```

- **Antenna end = far end from USB-C.** The USB shell and cable are metal.
- **Keyring hole:** NPTH ~4mm, in the top corner *opposite* the antenna,
  ≥2mm of board to the edge, copper keepout ~1mm around it. Never put it at
  the USB end, or the ring blocks the plug.
- **Buttons (SW1 RESET, SW2 BOOT)** must stay reachable after the OLED and
  battery are mounted. Put them at the USB end, which has to stay exposed
  anyway.
- **All SMT on the top side.** A single side means one assembly pass,
  which is cheaper.

---

## 2. Block by block

### RF + antenna (do this first, everything else fits around it)

| Rule | Source |
|---|---|
| AE1 in a board **corner**, long axis parallel to the edge, ~1mm in from it | Johanson p.3 |
| **6.5 × 6.5mm copper-free area** around AE1 on **both layers**. Use a KiCad Rule Area: keep out tracks, vias and zone fill, but allow footprints | Johanson p.3 |
| AE1 pin 1 (feed) faces the ground plane. Pin 2 (NC) gets its pad and solder but no connection | Johanson p.2 |
| U3 **pin 1 corner points at the antenna** | Espressif §1.4.4 |
| C15 (shunt, at pin 1) → L3 (series) → C14 (shunt) as close to pin 1 as possible, **zigzag** (the two caps not oriented the same way) | Espressif §1.4.4 |
| No 2nd-harmonic stub needed: "not required for 0402 and above", and these are 0402 | Espressif §1.4.4 |
| C14/C15 GND pads: a via right at each pad, solid connection (no thermal spokes) | Espressif §1.4.2 |
| RF trace from C14 to AE1: **top layer only, no vias, constant width, no branches, ≤4mm**, GND via fence on both sides at ~1mm pitch, solid bottom GND under it | Espressif §1.4.4 |
| Nothing else routed near the RF trace, on any layer | Espressif §1.4.9 |

### ESP32-C3 (U3) — pin sides and what goes on each

| Side | Pins | Place here |
|---|---|---|
| 1 | 1 RF · 2,3 VDD3P3 · 4,5 INT1/INT2 · 6 GPIO2 · 7 EN · 8 VBAT_SENSE | π network at pin 1, **C9 + C10 at pins 2/3**, R8 at 6, R7+C6 at 7, R15/R16/C19 near 8 |
| 2 | 9 SDA · 10 SCL · 11 RTC · 14 GPIO8 · 15 BOOT | C8 at 11, R14 at 14, R9 at 15. I2C heads toward U4 and the OLED pads |
| 3 | 17 VDD3P3_CPU · 18 VDD_SPI · 19–24 NC | C7 at 17, C11 at 18. No routing on this side, so it's free for the 3V3 feed |
| 4 | 25,26 USB · 29,30 XTAL · 31,32 VDDA | R3/R4 near 25/26, crystal off 29/30, **C20 + C21 at 31/32** |

- **EP (pin 33): ≥9 GND vias** (3×3 grid, 0.3mm drill), solid to the
  pour. Use a windowed paste pattern (~4 squares) so the QFN doesn't float
  on a solder blob.
- **Power:** 3V3 enters at **C9 (10µF) by pins 2/3**, then branches in a
  star **on the top layer** around the outside of the chip to each pin's
  own cap. Espressif: "a 10µF capacitor before the power trace enters the
  chip… then branch out in a star-shaped layout". Keep U2 close to that side
  so C9 doubles as the "main power entrance" cap. Side 3 (pins 19–24, all
  NC) has no other routing, so it's the natural path for the 3V3 branch to
  pins 17/18.
- Every decoupling cap sits on its own pin with a GND via at its pad.
  Cap first, then the via to the pin, never via → cap.

### Crystal (X1, C12, C13)

- **≥2mm gap between the crystal and the chip**, on the pin 29/30 side,
  toward the pin 25 end so it stays away from the RF corner.
- **No vias on XTAL_P/XTAL_N.** Short, direct, top layer.
- C12/C13 at the crystal's own pads, GND via right at each.
- **Nothing routed under the crystal on any layer.** Stitch GND vias
  around it. Keep it away from the antenna and from USB.

### USB (USBC1, D1, R1–R4)

- USB-C flush with the board edge, using the footprint's board-edge marker.
  EH shell tabs go to GND.
- **D1 (USBLC6) right behind the connector**, with a short, fat GND via.
- Tie DP1+DP2 and DN1+DN2 right at the connector. That needs one short
  bottom-layer crossover (every USB-C footprint does). Keep it under ~2mm,
  with a GND via next to each signal via.
- R3/R4 (22Ω) **near the chip side** (Espressif §1.4.8).
- D+/D− routed as a pair, equal length, on top over unbroken bottom GND.
  The ESP32-C3 is USB Full-Speed (12Mbps), so on traces this short,
  keeping the pair together matters more than hitting exactly 90Ω. On
  2-layer 1.6mm, true 90Ω isn't practical anyway.
- R1/R2 (CC 5.1k) right at the CC pins.

### Power path (U1, U2, Q1, D2, R13, C1–C5, LED1)

- Cluster at the USB end: USBC1 → C1/C3 → U1 and D2/Q1 → V_SYS → U2 → 3V3
  heading toward U3's pin 2/3 side.
- **C4 at U2 Vin, C5 at U2 Vout**, both within ~1mm of the pins.
- **C2 (10µF) right at U1 VBAT (pin 3).** It's the charger's stability cap.
- Q1, D2 and R13 next to each other between U1 and U2. Tracks at 0.4mm.
- U1 dissipates up to ~0.3W while charging, so give its VSS pin a copper
  pad and a couple of GND vias.
- BAT+ / BAT− pads (TP5/TP6) on an edge near U1, with **"+" and "−"
  clearly on silkscreen**. Reversed polarity kills the charger.

### Accelerometer (U4, C16–C18, R10)

- Near the middle of the board, **away from USB-C, the buttons, the keyring
  hole and the board edges**. Board flex from plugging in or pressing a
  button shifts an MEMS sensor's zero point.
- C16/C18 at VDD (pin 9), C17 at VDD_IO (pin 10).
- LGA-12, 0.5mm pitch: 0.15mm fan-out tracks, no vias under the part.

### Pads (TP1–TP6)

- OLED pads **TP1–TP4 in a row at 2.54mm pitch in your module's pin
  order**, so wires don't cross and the header can even solder straight
  in. Check your module first: some are GND-VCC-SCL-SDA, others
  VCC-GND-…
- Silk-label every pad.
- After soldering, glue over the wires for strain relief. That's the #1
  robustness item for something on a keyring.

---

## 3. Before ordering

- [ ] DRC clean, with "unconnected items" at zero.
- [ ] Antenna rule area empty of copper on both layers (check each layer
      on its own).
- [ ] No bottom-layer trace longer than a few mm, and none under U3, X1,
      the RF trace or AE1.
- [ ] Nothing routed under X1 or next to the RF trace.
- [ ] EP has ≥9 vias. Every cap has its GND via at the pad.
- [ ] USB-C front face at the board edge.
- [ ] Silkscreen: BAT +/−, OLED pin names, RST, BOOT.
- [ ] JLC CPL rotations checked in their preview (LCSC-library footprints
      are usually right, but check the QFN, SOT-23s, LED and diode
      polarity).
