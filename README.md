# SHAKE_FOB_REV-A

A PCB keychain: a shake-activated OLED "digital pet" fob. Sleeps at ~0 µA-class draw
until shaken, wakes and shows an emoji/gif on a small I2C OLED, advances to the next
one on a gentle shake, and sleeps again after 10 s idle. BLE included for a future
companion app to push new gifs. Charges and programs over USB-C. Built for JLCPCB
fab + assembly, optimized for the smallest board that still fits the parts.

## Key specs

| | |
|---|---|
| MCU | ESP32-C3FH4 (bare QFN32, 4 MB integrated flash, RISC-V, BLE 5) |
| Accelerometer | MMA8452QR1 (QFN-16 3×3 mm), transient (high-pass) wake interrupt, no polling needed. Replaced LIS2DH12TR, which is JLC "Standard PCBA only" |
| Charger | MCP73831T-2ACI/OT (SOT23-5), USB-C VBUS in, 147 mA charge rate (R_PROG = 6.8 kΩ) |
| 3V3 rail | XC6206P332MR (SOT23-3), ~1 µA Iq, 200 mA — sized for sleep-dominated duty |
| USB-C | TYPE-C-31-M-12, 16-pin, native USB D+/D− straight to the MCU (no CP2102/CH340) |
| Display | **off-board** — 0.96" 128×64 I2C OLED (SSD1306), 4 bare solder pads (GND/VCC/SCL/SDA), swappable |
| Battery | **off-board** — single-cell LiPo via 2 bare solder pads, user-sourced (the seller's cells come as bare leads, not a pre-terminated JST plug) |
| Buttons | RESET (EN→GND) and BOOT (GPIO9→GND), small SMD tactile — SuperMini-style |
| Board | 2-layer, target ≈ 25–30 × 18–22 mm, JLCPCB fab + SMT assembly |

All ICs above are on the JLCPCB parts library (LCSC part numbers in the BOM notes
below); the display and battery are intentionally *not* SMT parts — they connect
through headers/wires so either can be swapped without touching the PCB.

## BOM / JLCPCB parts library status

Checked against LCSC/JLCPCB directly (not from memory). Prices/stock are a snapshot
— reverify before ordering.

| Ref | Part | LCSC | JLCPCB library | Notes |
|---|---|---|---|---|
| U1 | ESP32-C3FH4, QFN-32-EP (5×5 mm) | C2858491 | Extended | 4233 in stock at check time |
| U4 | MMA8452QR1, QFN-16 (3×3 mm) | C11360 | Extended | Economic-PCBA OK, MSL1, 2,916 in stock. Replaced LIS2DH12TR (C110926: LGA, X-ray required → Standard PCBA only) |
| U3 | MCP73831T-2ACI/OT, SOT23-5 | C424093 | Extended (assumed) | not confirmed live, low risk either way |
| U4 | XC6206P332MR, SOT23-3 | C5446 | **Basic** | ~$0.02, ~1 µA Iq |
| U5 | USBLC6-2SC6, SOT23-6 | C7519 | Extended | USB ESD protection, use the genuine ST part |
| D2 | 1N4148WS, SOD-323 | C2128 | **Basic** | VBUS→SYS. Silicon, not Schottky, for nA reverse leakage on battery (see Power architecture) |
| Q1 | AO3401A P-MOSFET, SOT-23 | C15127 | **Basic** | BAT→SYS load-share switch (Microchip AN1149), ~14 mV drop vs ~0.3 V for a Schottky |
| R15, R16 | 1 MΩ 0402 battery-sense divider → GPIO3 | C26083 | **Basic** | + C19 100 nF; 2.1 µA |
| J1 | TYPE-C-31-M-12, USB-C 16-pin | C165948 | Extended | USB 2.0 subset only (VBUS/GND/D±/CC/SBU) |
| Y1 | 40 MHz crystal, 3225, C_L = 12 pF | **C5380316** (SOSET) | — | imported and confirmed 40 MHz on import; C13738 was mis-picked earlier (turned out to be 16 MHz) and has been removed |
| SW1, SW2 | TS342A2P tactile switch, 4×3×2 mm | C398055 | Extended | RESET + BOOT; checked for a Basic alternative, none found |
| TP1–TP4 | 4× bare solder pad (KiCad `TestPoint` lib) — OLED: GND/VCC/SCL/SDA | generic | n/a, not a real component | replaces a 2.54mm header — no connector to import, no BOM/CPL line |
| TP5–TP6 | 2× bare solder pad (KiCad `TestPoint` lib) — battery: BAT+/GND | generic | n/a, not a real component | replaces the JST-PH connector (below) — the actual battery source is bare leads, not a pre-terminated plug, so there's nothing to keep a connector for |
| ~~J3~~ | ~~S2B-PH-SM4-TB, SMD JST-PH 2-pin~~ | ~~C295747~~ | ~~Extended~~ | **dropped** — imported into the library, then superseded by TP5/TP6 once it turned out the battery isn't sold pre-terminated |
| ANT | Johanson 2450AT18A100E chip antenna | C89334 | — | in stock at check time; decided over a PCB trace, see Antenna below |
| — | RF matching, **chip-side only** (2×C 1.2–1.8pF + 1×L 2.0–3.0nH, 0201, pi network) | generic 0201 | Basic-class, commodity | antenna-side network deliberately dropped for a minimal BOM — see MCU wiring below |
| — | passives (0402/0603/0201 R/C) | generic | Basic-class, commodity | |

**11 Extended parts** after the two free swaps below (JLC BOM check,
2026-09-23): ESP32-C3FH4, MMA8452QR1, MCP73831, USBLC6-2SC6, TS342A2P,
USB-C (C165948), 40MHz crystal (C5380316), antenna (C89334), 1.5pF RF caps
(C1552), 2.2nH (C27122), 0402 LED (C71911). At $3 each that's ≈ **$33** in
loading fees. An earlier count of "5" was wrong. Free swaps with the same
footprint: 10k C25531 → **C25744** (R7–R9, R13, R14) and 100k C25530 →
**C25741** (R10), both Basic. Nothing else on the list has a Basic
equivalent in the same footprint.

**Assembly tier: Economic PCBA.** LIS2DH12TR (and its SC7A20 clone) is
flagged "Standard only" by JLC (LGA → X-ray, MSL3), so the accelerometer was
swapped to MMA8452QR1 (QFN, MSL1, Economic OK). It costs ~$1 more per part and
+3µA of sleep current, but saves ~$17 in Standard setup and the forced edge
rails.

## MCU wiring — verified against Espressif's datasheet + hardware design guidelines

Pulled `esp32-c3_datasheet_en.pdf` and the ESP32-C3 hardware design guidelines
directly (saved in [`datasheets/`](datasheets/)) rather than relying on memory.
Key points that affect the schematic:

- **Power pins**, each needs local decoupling: VDD3P3 (analog/RF, pins 2–3) — 10 µF
  + 0.1 µF (Espressif also suggests an LC filter inductor here for harmonic
  suppression — **dropped**, it's RF-certification margin rather than something
  needed for function, and the linear LDO feeding this rail is already low-noise);
  VDD3P3_RTC (pin 11) — 0.1 µF; VDD3P3_CPU (pin 17) — 0.1 µF; **VDD_SPI (pin 18)** —
  tie directly to 3V3 with a 1 µF cap, since the in-package flash on the FH4 needs
  VDD_SPI ≥ 3.0 V and this pin *cannot* be used as a GPIO on this variant. Add an ESD
  diode + ≥10 µF at the board's main power entrance too.
- **CHIP_EN**: must never float. Standard R=10 kΩ / C=1 µF RC delay to 3V3, RESET
  button pulls it to GND. Espressif's own note: on a slow/battery power rise, RC
  alone can be marginal — accepted as-is here (nearly every hobby ESP32 board ships
  with just RC), flagged as a known limitation rather than adding a supervisor IC.
- **Strapping pins** (GPIO2, GPIO8, GPIO9): GPIO9 gets an explicit pull-up
  (10 kΩ→3V3) *and* the datasheet explicitly warns not to put a capacitor on it, or
  the chip can drop into download mode — matters because BOOT button lands here.
  GPIO2 also gets a 10 kΩ pull-up ("recommended... due to glitches" even though it
  doesn't strictly gate boot mode). GPIO8 gets a 10 kΩ pull-up (R14): download boot needs GPIO8 = 1 (Table 3-3).
- **Crystal**: 40 MHz is compulsory (no internal option), ±10 ppm. Standard 2-pad
  crystal + 2 load caps. Espressif also suggests a 24 nH series inductor on the
  XTAL_P trace for harmonic suppression — **dropped**, same reasoning as the
  VDD3P3 filter above: their own guideline calls the value an "initial
  suggestion... adjust after an overall test," i.e. margin, not a requirement.
  ≥2 mm gap from the chip's clock pin, no vias on the clock trace itself, keep
  it away from the RF trace.
  **Load cap value, corrected:** the formula is `C_L = (C1×C2)/(C1+C2) + C_stray`
  (checked directly against Espressif's live HTML page — the PDF's text extraction
  had jumbled the fraction and put C_stray inside the denominator, which gave a
  wrong answer the first time around). With C1=C2=C, C_stray≈3 pF (typical PCB
  estimate), and our crystal's C_L=12 pF: `C = 2×(C_L − C_stray) = 2×(12−3) =
  18 pF`. **C1=C2=18 pF**, not the earlier 27 pF.
- **RF matching — deliberately minimal, one network not two.** Espressif's
  checklist describes two possible networks: a chip-side CLC ("must be
  placed close to the chip," no exception given) and a separate antenna-side
  CLC (which *does* have an explicit skip condition, if the antenna's
  impedance is already known to be 50Ω). The fully-by-the-book version of
  this design would have both — went there briefly, then cut back down by
  explicit request for a minimal board. **Kept the chip-side network only**
  (Espressif's generic bare-chip pi values: 1.2–1.8 pF / 2.0–3.0 nH /
  1.8–1.2 pF, 0201): a bare silicon RF pin with no matching at all is
  typically a bigger mismatch than a purpose-built antenna's nominal
  impedance drifting somewhat from board-layout differences, so this is the
  half that protects against the larger problem. **Dropped the antenna-side
  network** (Johanson's own T-network for this specific antenna, which their
  datasheet does recommend — see `docs/SCHEMATIC_BOM.md` Block 4e for the
  values, kept there for reference even though not populated). **Accepted
  trade-off, not a free simplification**: the antenna's real impedance on
  this board won't exactly match Johanson's 50Ω spec (measured on their own
  eval board), and that drift goes uncorrected — some range/efficiency traded
  for a smaller BOM, reasonable for a close-range, non-certified BLE keychain.

  Full derivation and the dropped network's values (kept for reference) in
  `docs/SCHEMATIC_BOM.md` Block 4e.
- **USB (GPIO18/19 = D−/D+)**: 22 Ω series resistors close to the chip; footprints for
  optional shunt caps and a D+ pull-up left unpopulated unless startup instability
  shows up on the bench.

### Antenna — decided: Johanson chip antenna

**Decision (confirmed with user 2026-09-22):** Johanson **2450AT18A100E** ceramic
chip antenna, LCSC C89334, in stock, ≈$0.54. The guidelines are explicit that a PCB
trace antenna needs EM simulation and real-world validation to get right — Espressif
doesn't publish a generic copy-paste trace for an arbitrary board shape, and
freehand-copying the SuperMini's antenna from a photo onto a different stackup has a
real chance of detuning it with no way for us to check. A chip antenna is a
purchasable SMD part with a vendor-validated footprint and matching network from
Johanson's own application note — a few cents of BOM for a much higher chance the
radio just works, with no lab equipment required. Still needs a copper/component
keep-out under and around it (per Johanson's app note), smaller than a full
PCB-trace keepout, so it doesn't reopen the board-size problem.

Note: the SuperMini board itself uses **ESP32-C3FN4**, which is now
**NRND (Not Recommended for New Designs)**. Good thing this board isn't cloning its
BOM — FH4 (already our pick) is the current, stocked part; "H" vs "N" also aren't
footprint-compatible, so a literal SuperMini clone wouldn't have dropped in anyway.

## Power / control architecture

```
USB-C VBUS (5V) ──┬──► MCP73831 ──► BAT ──► battery pads (TP5/TP6)
                  │                   │
                  │                   ├──► R15/R16 1M:1M ──► GPIO3 (battery sense)
                  │                   │
                  │                   └──► Q1 AO3401A (D→S) ──┐
                  │                          gate ◄── VBUS    │
                  ├──► D2 1N4148WS ─────────────────────────┴──► SYS ──► XC6206 ──► 3V3 ──► ESP32-C3, MMA8452Q, OLED
                  └──► R13 10k ──► GND (Q1 gate pull-down)
   CC1/CC2 ──5.1k──GND
   D+/D− ──────────────► MCU native USB

MMA8452Q INT1 ──► GPIO0 (RTC-capable, deep-sleep wake source, active-high)
MMA8452Q INT2 ──► GPIO1 (spare, wired for future use)
```

**Load sharing (Microchip AN1149).** USB present: Q1's gate is at VBUS, so
it's off. D2 feeds SYS and the battery charges alone, which lets the
charger terminate properly. USB absent: R13 pulls the gate low, Q1 turns
fully on, and SYS = BAT − ~14 mV. The board runs from USB with no battery
installed, and the battery never sees raw VBUS. Full reasoning and pin-out
are in [`docs/SCHEMATIC_BOM.md`](docs/SCHEMATIC_BOM.md) Block 2.

**Wake GPIO: GPIO0** (physical pin 4, `XTAL_32K_P`). ESP32-C3's RTC-IO pins — the
only ones that can wake the chip from deep sleep — are GPIO0–GPIO5 (the pins
powered by VDD3P3_RTC; datasheet §2.5, Table 2-1). Ruled out the others: GPIO2 is
a strapping pin (already has a pull-up for glitch immunity — simpler not to also
share it with an interrupt input at boot); GPIO4/GPIO5 double as JTAG (MTMS/MTDI);
GPIO0/GPIO1 are the pins for the *optional* 32.768 kHz RTC crystal, which this
board isn't populating, and the datasheet explicitly says those pins "can be used
as GPIOs" when that crystal is skipped (§1.3.5) — so GPIO0 is genuinely spare, not
a compromise. The MMA8452Q's INT pins are push-pull and always driven, so
**no pull resistor on either INT pin**. The old 100 kΩ pull-down (R10) is
deleted. It would fight the chip's power-on default (active-low, so idle
high) and waste 33 µA until firmware sets IPOL = 1.

- **Wake-on-shake is hardware, not polled.** The MMA8452Q's transient detector
  (high-pass filtered, so gravity and slow tilting are ignored) runs at 12.5 Hz in
  low-power mode (6 µA). A vigorous shake above ~1.5 g latches INT1, which wakes the
  ESP32-C3 from deep sleep. Once awake, firmware reprograms the same transient channel
  to a gentle threshold (~0.5 g at 50 Hz) for "next gif", then restores the wake
  settings before sleeping. There's only one transient channel, and it's all both
  gestures need. INT2 is wired but spare. Register values are in
  docs/SCHEMATIC_BOM.md Block 5.
- **Why a P-FET and not a second Schottky on the battery side.** The earlier
  D2+D3 diode-OR put a ~0.3V Schottky drop in the battery path. That raised
  the usable-battery floor to ~3.45V active, or ~3.6V during BLE. Q1 drops
  ~14mV, which puts the floor at **~3.1–3.2V active and ~3.3V during BLE**.
  Below that a LiPo has only a few % left, so this is effectively the whole
  cell. D2 is a **silicon** 1N4148WS on purpose: on battery it sits
  reverse-biased at ~4V, and the 1N5819WS Schottky leaks ~6–7µA there at
  25°C (read off its datasheet curve). That's over half the sleep budget.
  The 1N4148WS leaks nA. Its higher forward drop only applies on USB, where
  there's headroom to spare.
- **XC6206 (200mA) stays, with two firmware rules.** The ESP32-C3 datasheet
  only tables Wi-Fi TX current: **335mA peak @ 21dBm**, far over 200mA. So:
  **never enable Wi-Fi**, and **cap BLE TX at 0dBm**. The datasheet has no
  BLE figure, so measure the real peak at bring-up. Normal operation (CPU +
  OLED, no radio) is ~40–45mA, comfortably inside the rating. RT9013 (500mA)
  was rejected because its ~25µA Iq would roughly triple sleep current. An
  earlier "~650mV droop at 10µF, go to 47µF" derivation was withdrawn: it
  rested on an invented 50µs LDO response time. C9 = 10µF + C10 = 0.1µF is
  Espressif's reference decoupling for VDD3P3.
- **GPIO8 pull-up (R14, 10k to 3V3).** It's a strapping pin, and download
  mode needs GPIO8 = 1. In deep sleep the USB-CDC port disappears, so BOOT +
  RESET is the recovery path, and it must be reliable.
- **Battery sense (R15/R16/C19 → GPIO3).** Lets firmware stop waking the
  display below ~3.3V and show a battery icon, instead of brownout-looping
  the cell down to its protection cutoff.
- **No physical power switch.** Sleep budget, every figure sourced from the actual
  datasheet (see Battery life below, not hand-waved): **≈14.4 µA typical, board only**. Shelf
  drain from our own electronics is a non-issue at that level — LiPo self-discharge
  dominates over it. Revisit if a firmware bug (e.g. polling instead of interrupt-driven
  wake) makes this wrong.
- **No onboard battery protection IC.** Assumes the LiPo cell has its own protection
  PCB, which is standard for small hobby packs. **Confirm this once a battery is
  picked** — an unprotected cell needs a DW01+FS8205 (or similar) added.

## Battery life — 300 mAh cell

Every current figure below is from the actual component datasheet (all saved in
[`datasheets/`](datasheets/)), not estimated:

| Contributor | Typ. current | Source |
|---|---|---|
| ESP32-C3 deep-sleep (RTC timer + RTC memory only) | 5 µA | Espressif datasheet, Table 5-9 |
| MMA8452Q low-power mode, ≤12.5 Hz ODR (watching for a shake) | 6 µA | NXP datasheet, Table 3 |
| XC6206 LDO quiescent current | 1.0 µA | Torex XC6206 series spec (converged across distributor-hosted copies; direct Torex PDF was blocked from this environment) |
| MCP73831 leakage into BAT when USB is unplugged | 0.25 µA (2 µA max) | Microchip datasheet, "Battery Discharge Current," V DD < (V BAT − 50 mV) condition — **not** the 53 µA figure floating around online, which is a different spec ("Charge Complete, No Battery," current from V DD, not from the battery) |
| D2 reverse leakage, 1N4148WS @ ~4 V | ~0.01 µA | nA-class. A 1N5819WS here would be ~6–7 µA (Hottech datasheet curve) |
| Battery divider R15 + R16 (2 MΩ) | 2.1 µA | 4.2 V / 2 MΩ |
| Q1 / R13 | 0 | VBUS is 0 V on battery |
| **Total sleep current (board)** | **≈14.4 µA typ** | **+ OLED module in display-off (not budgeted — measure it)** |

**Pure shelf life** (never touched): the cell's own protection IC (~3 µA,
DW01-class) and LiPo self-discharge (~1–2 %/month ≈ 4–8 µA equivalent) are
as big as the board itself. A realistic shelf estimate, cell untouched, is
**~1–1.5 years**, minus whatever the OLED draws asleep.

**Real-world battery life is dominated by usage, not sleep current.** Per wake event
(OLED + MCU active for the spec'd 10 s, no radio — BLE is rare per your last note):
ESP32-C3 active ≈ 20 mA (Espressif Table 5-8, Modem-sleep/CPU-running range is
13–23 mA depending on clock and load) + SSD1306 OLED ≈ 20 mA (content-dependent,
typical hobbyist figure, not datasheet-sourced) ≈ **40 mA for 10 s ≈ 0.11 mAh/wake**.

| Wakes / day | mAh/day (wakes + sleep baseline) | Battery life |
|---|---|---|
| 10 (a few deliberate check-ins) | ~1.6 | **~6 months** |
| 30 (frequent play + some incidental jostling) | ~3.8 | **~2.5 months** |
| 100 (worst case — threshold too sensitive, triggers on walking/bag movement) | ~11.6 | **~26 days** |

**The single biggest lever on battery life is the shake-detection threshold**, not
any hardware choice already made — a threshold tuned to reject normal carrying
motion (walking, keys jingling in a pocket) versus one that only catches a
deliberate vigorous shake is roughly a 4–10× difference in real-world runtime. This
needs bench tuning once hardware exists; it can't be fully predicted on paper.

## Architecture decisions

| Decision | Rationale |
|---|---|
| Bare ESP32-C3FH4, not the MINI-1 module | User pointed at the ESP32-C3 "SuperMini" board as the size reference — that board uses the bare chip, not the pre-shielded module. Smaller and cheaper, at the cost of doing the RF front-end ourselves (see MCU wiring / Antenna below). |
| Chip antenna, not a hand-copied PCB trace | Confirmed with user. Espressif's own guidelines say a PCB trace antenna needs EM simulation + real hardware validation, which we can't do. A vendor-validated ceramic chip antenna (Johanson 2450AT18A100E, ~$0.54) is a few cents for much higher confidence it just works — reasonable even though BLE itself is a rarely-used, nice-to-have feature here, precisely because it's cheap enough not to be worth the risk either way. |
| Antenna keepout: tighter than Espressif's full 15 mm recommendation | 15 mm clearance in every direction would dominate the board size on something this small. The chip antenna's own keep-out (per its application note) is smaller than the bare-trace figure, and SuperMini-class boards prove a tight keepout still works for short-range BLE. Accepted trade: reduced RF range, irrelevant for a phone held next to a keychain. |
| MMA8452QR1 over LIS2DH12TR | LIS2DH12TR (and the SC7A20 clone) are JLC "Standard PCBA only" (LGA → X-ray, MSL3). The MMA8452Q is QFN, MSL1, Economic-assemblable, in stock, and has a high-pass transient detector made for shake wake. Costs: 3×3 mm vs 2×2 mm, ~$1 more, and 6 µA vs 3 µA asleep. The 2×2 MMA8652FC/MMA8653FC would be better but were out of stock (2026-09-23). |
| XC6206P332MR over AMS1117 / a plain 662k-style LDO | JLCPCB Basic part, ~1 µA quiescent current. AMS1117's ~5 mA quiescent draw alone would blow the sleep budget by >250×. |
| MCP73831 over TP4056 | SOT23-5 is smaller than TP4056's SOP-8, and board area is the constraint here. Trade-off: no onboard load-disconnect/protection — see the protection-IC note above. |
| Native USB (no CP2102/CH340 bridge) | ESP32-C3 has an on-chip USB-Serial-JTAG controller; wiring D+/D− straight to it gives USB-CDC programming and a serial console for free, and drops a chip + its passives from the BOM. |
| OLED and battery off-board via solder pads | Per instruction — keeps the option to change display size later without a respin, and neither part is realistically JLCPCB-SMT-placeable-and-reliable at this end of the market anyway (small COG/FPC displays are usually hand-placed even on boards that do put them in the BOM). Pads instead of connectors on both, once it was clear neither the OLED nor the battery arrives pre-terminated for one. |

## Open items (before this is ready for schematic capture)

**Resolved this pass:**
- ~~Antenna approach~~ → **decided and confirmed:** Johanson 2450AT18A100E chip antenna
- ~~40 MHz crystal~~ → **SOSET C5380316**, confirmed 40 MHz on import (an earlier candidate, YXC C13738, turned out to be 16 MHz and was removed from the library)
- ~~Library import~~ → all 9 distinctively-numbered parts imported into `ESP32_C3_FOB/libs/lcsc/` via the LCSC manager plugin, symbol+footprint+3D model each — see `docs/SCHEMATIC_BOM.md` for the KiCad symbol/footprint names
- ~~RF matching network~~ → settled on **chip-side pi network only** (Espressif's generic values), one network not two — antenna-side T-network (Johanson's values) deliberately dropped for a minimal BOM, accepted as a real trade-off not a free simplification. VDD3P3 filter and crystal series inductors also dropped as unneeded RF-certification margin.
- ~~JLCPCB part availability~~ → full table above, all parts orderable today
- ~~Sleep-current budget~~ → re-derived from actual datasheets: ≈12.25 µA typ (see Battery life) — corrects the earlier hand-waved 17 µA figure
- ~~Battery life estimate~~ → see Battery life section; dominated by wake frequency, not sleep current
- ~~Wake GPIO~~ → **GPIO0**, see Power/control architecture above for why
- ~~R_PROG~~ → **battery confirmed at 300 mAh; R_PROG = 6.8 kΩ → 147 mA (≈0.5C)**,
  from MCP73831 datasheet §5.2.2: `I_REG(mA) = 1000 × V / R_PROG(kΩ)`. 0.5C chosen
  over 1C (300 mA, R_PROG = 3.3 kΩ) for better cycle life on a small cell — swap one
  resistor if faster charging matters more than longevity.

**Still open:**
- **Board outline and JLCPCB panelization** — anything under 70×70 mm needs a panel
  (mouse-bites or V-cut) for SMT assembly; this board will need one designed once
  the outline is fixed.
- Charge-status LED on MCP73831 STAT — included by default, cut if it doesn't fit.
- CHIP_EN RC-only power-up timing on battery power — accepted risk, see MCU wiring above.

## Repository layout

| Path | Contents |
|---|---|
| `SHAKE_FOB_REV-A.kicad_pro/.kicad_sch/.kicad_pcb` | KiCad project (not created yet) |
| `libs/lcsc/` | Project-local LCSC symbols/footprints/3D models |
| `docs/` | Working notes |

## Status

**Architecture and BOM defined. Schematic capture not started.**
#   S H A K E _ F O B _ R E V - A  
 