# Schematic component checklist — SHAKE_FOB_REV-A

Parts + wiring, block by block. Pin names/numbers are from the actual
imported symbols. Reference designators are suggestions, renumber freely.

**Routing order:** GND (power symbol) → 3V3, VBUS, BAT, SYS (local labels) →
SDA, SCL (local labels) → Blocks 1–7 local wiring below → unused U3 pins
(12, 13, 16, 19–24, 27, 28) + USB-C SBU1/SBU2 get No-Connect flags → ERC
→ export netlist. **GPIO8 (pin 14) and GPIO3 (pin 8) are NOT No-Connect
pins.** GPIO8 needs a pull-up (Block 4c), GPIO3 is battery sense (Block 2c).

**Power nets, at a glance:** VBUS (raw 5V from USB-C) → BAT (charger output
/ the cell itself, TP5) → **SYS** (LDO input — fed from VBUS through D2 when
USB is present, from BAT through P-FET Q1 when it isn't) → 3V3 (everything
else). BAT and SYS are deliberately different nets — see Block 2.

**Ref-des / size note:** Blocks 1–2 use the schematic's real ref-des. In
Blocks 4–7, **U5 = schematic D1** (USBLC6), **ANT1 = AE1**, **Y1 = X1**,
and in 4e C14/C15 are swapped vs the schematic. Both are 1.5pF, so that
doesn't matter electrically. **All passives are 0402.** JLC Economic
PCBA only places parts down to 0402, so the last three 0201s (R1, R2, R6)
must change to 0402. See LAYOUT.md §0.

---

## Block 1 — USB-C input + ESD

Ref-des below match the actual schematic.

| Ref | Part | Value/Package | LCSC |
|---|---|---|---|
| USBC1 | TYPE-C-31-M-12 | USB-C receptacle, 16-pin | C165948 |
| R1, R2 | Resistor | 5.1 kΩ, **0402** (was 0201 C143995 — change it) | **C25905** |
| D1 | USBLC6-2SC6 | SOT23-6 | C7519 |
| C1 | Ceramic cap | 10 µF 6.3V X5R, 0402 | C15525 |
| C3 | Ceramic cap | 1 µF, 0402 | C52923 |

| Pin | → |
|---|---|
| USBC1.VBUS (both pairs) | **VBUS** net |
| USBC1.GND (both pairs) + 4× `EH` tabs | **GND** |
| USBC1.CC1 (A5) | R1 → GND |
| USBC1.CC2 (B5) | R2 → GND |
| USBC1.DP1 (A6) + DP2 (B6) | tied together → D1.pin3 |
| USBC1.DN1 (A7) + DN2 (B7) | tied together → D1.pin1 |
| C1, C3 | VBUS ↔ GND |
| D1.pin2 | GND |
| D1.pin5 | VBUS |
| D1.pin6 | → R3 → USB_D− → U3.GPIO18 (25) |
| D1.pin4 | → R4 → USB_D+ → U3.GPIO19 (26) |
| SBU1 (A8), SBU2 (B8) | No-Connect |

DP1+DP2 must be tied together, same for DN1+DN2 — connector is reversible,
skip one pair and flipped-cable orientation breaks.

---

## Block 2 — Charger + load sharing

### 2a. Charger (MCP73831)

| Ref | Part | Value/Package | LCSC |
|---|---|---|---|
| U1 | MCP73831T-2ACI/OT | SOT23-5 | C424093 |
| R5 | Resistor | 6.8 kΩ, 0402 | C25917 |
| C2 | Ceramic cap | **10 µF**, 0402 (**change from 1µF**) | C15525 |
| LED1 | LED, red | 0402 | C71911 |
| R6 | Resistor | 1 kΩ, **0402** (was 0201 C100125 — change it) | **C11702** |

| Pin | → |
|---|---|
| U1.VDD (4) | VBUS |
| U1.VSS (2) | GND |
| U1.VBAT (3) | **BAT** net → TP5, Q1 drain, R15 (2c) |
| U1.PROG (5) | R5 → GND |
| U1.STAT (1) | R6 → LED1 cathode |
| LED1 anode | VBUS |
| C2 | BAT ↔ GND |

**Charge current:** I_REG = 1000 V / R_PROG(kΩ) = 1000/6.8 = **147mA** =
0.49C for a 300mAh cell. That's a safe rate. Charger dissipation at
worst case (5V in, 3.0V cell) is 2V × 0.147A = 0.29W, fine for SOT23-5.

**C2 must be ≥4.7µF.** MCP73831 datasheet, VBAT pin: "Bypass to VSS with a
minimum of 4.7µF to ensure loop stability when the battery is
disconnected." Right now BAT has only C2 (1µF) + C4 (1µF), and C4 is moving
to SYS. Change C2 to 10µF (C15525, same part as C1/C9/C18, so no new BOM
line). A 6.3V 0402 part keeps ~4–5µF effective at 4.2V bias, which meets
the minimum.

STAT sinks (LED on) while charging and goes Hi-Z at charge-complete.
**With USB in and no battery, LED1 flickers.** The charger keeps cycling
into an empty cap, which is normal MCP73831 behavior and harmless.

### 2b. Load sharing: D2 + Q1 + R13 (Microchip AN1149)

This is the standard MCP73831 load-sharing circuit from Microchip's app
note, used on Adafruit/SparkFun LiPo boards. It covers three cases:

1. USB in, battery in → system runs from USB, battery charges alone
   (charger terminates properly instead of floating the cell at 4.2V forever
   under system load).
2. USB in, no battery → system runs from USB.
3. USB out → system runs from the battery with ~5–15mV loss.

| Ref | Part | Value/Package | LCSC | JLCPCB |
|---|---|---|---|---|
| D2 | **1N4148WS** | Si switching diode, 150mA, SOD-323 | C2128 | Basic |
| Q1 | AO3401A | P-MOSFET, −30V, R_DS(on) 85mΩ @ V_GS −2.5V, V_th −0.9V, SOT-23 | C15127 | Basic |
| R13 | Resistor | 10 kΩ, 0402 | C25744 (same as R7–R9) | Basic |

| Pin | → |
|---|---|
| D2 anode | VBUS |
| D2 cathode | **SYS** |
| Q1 pin 3 (D) | **BAT** |
| Q1 pin 2 (S) | **SYS** |
| Q1 pin 1 (G) | **VBUS** |
| R13 | VBUS ↔ GND (gate pull-down) |

After import, check that the symbol's pin names match G=1, S=2, D=3. That's
the standard SOT-23 MOSFET pinout, but wire by name, not by position.

Drain goes to the battery and source to the load. That's backwards from a
normal high-side switch, and it's on purpose: the body diode then points
BAT→SYS.

- **USB present:** SYS = VBUS − V_F(D2) ≈ 4.0–4.6V. Q1 gate = VBUS, so V_GS
  = +V_F(D2) > 0 and Q1 is always off. Body diode is reverse-biased or at
  most ~0.2V forward (BAT ≤ 4.2V), so the battery is isolated.
- **USB unplugged:** R13 pulls the gate to 0V. The body diode conducts
  first, SYS ≈ BAT − 0.6V, V_GS ≈ −3V, and Q1 turns fully on. Drop is then
  I × R_DS(on) = 170mA × 85mΩ = **14mV** worst case. D2 blocks backfeed into
  USB, and the body diode bridges the handover so the rail never drops out.
- **R13 = 10k, not 100k:** VBUS has ~5µF effective on it (C1 at 5V bias +
  C3). With 10k it decays in ~50ms after unplug, where 100k takes ~0.5s with
  the body diode carrying the load. It also holds Q1's gate low against
  D2's reverse leakage. Costs 0.5mA from USB while plugged in, and zero on
  battery.

**Why D2 is a 1N4148WS and not a Schottky.** With USB unplugged, D2 sits
reverse-biased at ~BAT voltage, and its leakage drains the battery through
R13 around the clock. Measured off the 1N5819WS (C191023) datasheet curve:
**~6–7µA at 4V/25°C, about 120µA at 100°C**. That's over half the entire
sleep budget, and it gets worse in a warm pocket. The 1N4148WS leaks in
the nA range at 4V. D2's forward drop doesn't matter: it only conducts
when USB is present, and 5V − 1V still leaves 0.7V of headroom over the
3.3V LDO. Trade-off accepted: 150mA average rating vs a load of ~40–80mA,
with short BLE peaks well inside its 2A surge rating. Same SOD-323
footprint.

**Why this replaced the D2+D3 diode-OR:** a Schottky in the battery path
(the old D3) drops ~0.25–0.35V at 50–170mA, and it drops it in the
battery-powered mode the keychain spends 99% of its time in. Q1 does the
same job for ~0.01V at zero sleep cost. BQ2407x-class power-path ICs were
rejected (QFN, +4.3µA sleep, still needs the LDO). A second LDO with a
diode-OR after regulation was rejected too: the diode would drop the 3.3V
rail itself to ~3.0V permanently.

### 2c. Battery voltage sense — recommended

| Ref | Part | Value/Package | LCSC |
|---|---|---|---|
| R15, R16 | Resistor | 1 MΩ ±1%, 0402 | C26083 (Basic) |
| C19 | Ceramic cap | 100 nF, 0402 | C1525 (same as C7) |

| Pin | → |
|---|---|
| R15 | BAT ↔ **VBAT_SENSE** |
| R16 | VBAT_SENSE ↔ GND |
| C19 | VBAT_SENSE ↔ GND |
| U3.GPIO3 (8) | VBAT_SENSE (ADC1_CH3) — **remove its No-Connect flag** |

VBAT_SENSE = BAT/2, so 4.2V reads as 2.1V, inside the ADC's 0–2500mV range
at 11dB attenuation. C19 is the charge reservoir for the ADC's sampling cap,
since a 500kΩ source can't feed it directly. Read once per wake, after the
node has settled (τ = 50ms).

**Why it's worth 2.1µA:** without it, firmware can't see the battery at
all. The LDO drops out, and the ESP32 brownout-resets every time you shake
it, until the cell's protection IC cuts at ~2.5V. That deep-discharges the
LiPo every cycle. With it, firmware refuses to wake the display below
~3.3V and can draw a battery icon. Cost is 3 small parts plus 2.1µA,
more than repaid by the ~7µA saved on D2.

---

## Block 3 — 3V3 rail (XC6206)

| Ref | Part | Value/Package | LCSC |
|---|---|---|---|
| U2 | XC6206P332MR | SOT23-3 | C5446 |
| C4, C5 | Ceramic cap | 1 µF, 0402 | C52923 |

| Pin | → |
|---|---|
| U2.Vin (3) | **SYS** (D2 cathode + Q1 source, Block 2 — not BAT directly) |
| U2.GND (1) | GND |
| U2.Vout (2) | **3V3** net |
| C4 | Vin ↔ GND (now on the SYS node) |
| C5 | Vout ↔ GND |

---

## Block 4 — ESP32-C3FH4 core

| Ref | Part | Value/Package | LCSC |
|---|---|---|---|
| U3 | ESP32-C3FH4 | QFN-32-EP 5×5mm | C2858491 |

### 4a. Power

| Pin | → |
|---|---|
| VDD3P3 (2,3) | 3V3 — C9 (10µF) + C10 (0.1µF), direct, no filter inductor (dropped — see 4d) |
| VDD3P3_RTC (11) | 3V3 — C8 (0.1µF) |
| VDD3P3_CPU (17) | 3V3 — C7 (0.1µF) |
| VDD_SPI (18) | 3V3, direct tie — C11 (1µF) |
| VDDA (31,32) | 3V3 — **C20 (1µF, C52923) + C21 (10nF, C15195) — add** |
| EP (33) | GND, ≥9 vias |

**No separate bulk cap. C9 (10µF) + C10 (0.1µF) is Espressif's own
reference value for VDD3P3.** An earlier "~650mV droop at 10µF" estimate
was wrong in two ways. It treated the full 130mA BLE peak as a step, when
the LDO is already supplying ~40mA before the burst, so the real step is
~90mA. It also assumed the LDO delivers nothing for 50µs, and nothing
backed that figure. Don't size caps off it. The real BLE-at-low-battery
risk is LDO dropout plus the 200mA limit. The Q1 fix (Block 2) and the BLE
TX-power cap (below) handle that.

**VDDA needs its own caps.** Espressif's reference schematic (hardware
design guidelines, Fig. 1) puts **1µF + 10nF on VDDA (31/32)**. An earlier
version of this doc said C9/C10 could serve VDDA by sitting "at the corner".
That doesn't work: RF pin 1 and its matching network occupy exactly the
corner between pin 32 and pin 2. Add C20 (1µF, C52923, same part as C3–C6)
and C21 (10nF, C15195, Basic) right at pins 31/32, with a GND via at each
cap.

**FIRMWARE RULES that keep the XC6206 (200mA max) in spec:**

1. **Never enable Wi-Fi.** The ESP32-C3 datasheet (Table 5-7) lists
   **335mA peak** for Wi-Fi TX at 21dBm. That's far over 200mA, and the
   rail will sag and brownout-reset. It won't cause damage, just resets.
   Watch for Arduino examples that turn Wi-Fi on by default.
2. **Cap BLE TX power** at 0dBm (`esp_ble_tx_power_set(..., ESP_PWR_LVL_N0)`
   or the NimBLE equivalent). The datasheet gives no BLE current figure, so
   the earlier "~173mA worst case" was an estimate. Measure the real peak
   with the scope and a shunt at bring-up. Range at 0dBm is plenty for a
   keychain.

The RT9013 (500mA) was rejected because its ~25µA Iq would roughly triple
the board's sleep current, while these two firmware rules cost nothing.

**Battery cutoff with the LDO** (ESP32-C3 needs ≥3.0V; XC6206 dropout is
~250mV @ 100mA, roughly proportional to current):

| Load | Old Schottky D3 | Q1 P-FET (now) |
|---|---|---|
| Active, display on, ~40–80mA | ~3.4–3.5V | **~3.1–3.2V** |
| BLE burst @ 0dBm, ~100mA | ~3.6V | **~3.3V** |

Below ~3.3V a LiPo has only a few % of its capacity left, and the cell's
protection IC cuts around 2.5–3.0V. So ~3.2V is effectively the whole
battery. Going to 2V isn't possible (ESP32-C3 minimum is 3.0V) and would
damage the cell anyway. Firmware should stop at ~3.3V using the Block 2c
sense.

### 4b. CHIP_EN

| Pin | → |
|---|---|
| CHIP_EN (7) | R7 → 3V3 · C6 → GND · SW1 → GND |

### 4c. Strapping

| Pin | → |
|---|---|
| GPIO2 (6) | R8 → 3V3 only |
| GPIO9 (15) | R9 → 3V3 · SW2 → GND · **no capacitor, ever** |
| GPIO8 (14) | **R14 (10 kΩ, 0402, C25744 — same as R7–R9) → 3V3** — remove the No-Connect flag |

**GPIO8 bug fix.** ESP32-C3 datasheet Table 3-3: Joint Download Boot needs
**GPIO8 = 1 and GPIO9 = 0**. GPIO8 has no internal pull (Table 3-1:
"Floating"). With it floating, holding BOOT + tapping RESET may not enter
download mode. That matters on this board: in deep sleep the USB-CDC port
disappears, so if firmware sleeps immediately or crashes, the BOOT button
is the only way back in. The SuperMini and Espressif dev kits hold GPIO8
high for exactly this reason. One resistor.

### 4d. Crystal

| Pin | → |
|---|---|
| XTAL_P (30) | Y1.pin1 directly — node also has C12 → GND |
| XTAL_N (29) | Y1.pin3 directly, node also has C13 → GND |
| Y1.pin2, pin4 | GND |

**L2 dropped.** Espressif lists the 24nH series inductor on XTAL_P as
harmonic-suppression margin for RF certification, not something the crystal
needs to function — their own guideline calls the value an "initial
suggestion... adjust after an overall test," i.e. it's already tunable/
optional by their own framing. Not chasing certification here, so skipped.

### 4e. RF matching — minimal: chip-side network only

**Deliberately minimal, one network not two.** Espressif's checklist
describes two possible networks (chip-side CLC and antenna-side CLC), and
the fully-by-the-book version of this design would have both. Cut back to
one for a genuinely minimal board — **kept the chip-side network, dropped
the antenna-side one.** Reasoning: a bare silicon RF pin with *no* matching
at all is typically a much larger mismatch than a purpose-built antenna's
own nominal impedance drifting somewhat from board-layout differences — so
if only one network stays, this is the one protecting against the bigger
problem. **Accepted trade-off, stated plainly**: the antenna's real
impedance on this specific board layout won't exactly match Johanson's
50Ω spec (measured on their own eval board), and that drift goes
uncorrected. For a close-range, non-certified BLE keychain, that's a
reasonable amount of range/efficiency to trade for a smaller BOM — not
"no downside," an actual accepted cost.

| Ref | Value/Package |
|---|---|
| C14 | 1.5 pF, 0402 C1552 (range 1.2–1.8 pF) |
| L3 | 2.2 nH, 0402 C27122 (range 2.0–3.0 nH) |
| C15 | 1.5 pF, 0402 C1552 (range 1.2–1.8 pF) |

Shunt-series-shunt (pi), placed close to U3: **node A: C14 → GND, and → L3**
→ **node B: C15 → GND, and → 50Ω trace straight to ANT1.pin1** — no
antenna-side network, direct connection from here.

| Pin | → |
|---|---|
| U3.LNA_IN (1) | node A (above) |
| node B (above) | 50Ω trace, direct → ANT1.pin1 (ANT, the antenna feed) |
| ANT1.pin2 | **True No-Connect** — matches Johanson's datasheet exactly, which labels this pin "NC," not GND. Mark it with a No-Connect flag in the schematic. The footprint pad is still there and still gets soldered during reflow regardless of net assignment, so the datasheet's "must be soldered for anchoring" requirement is satisfied either way — NC just means no trace/net, not no solder joint. Don't tie it to GND; that adds a connection Johanson never specified. |

Three RF-specific passives, not six. L1 and L2 are unused ref-des. C19 is
reused for the battery-sense filter cap (Block 2c).

### 4f. USB at the chip

| Pin | → |
|---|---|
| GPIO18 (25) | R3 → U5.pin1/6 (I/O1) |
| GPIO19 (26) | R4 → U5.pin3/4 (I/O2) |

Optional shunt caps + D+ pull-up footprints: unpopulated unless USB is flaky
on the bench.

### 4g. Do NOT connect

| Pins | Treatment |
|---|---|
| SPIHD/SPIWP/SPICS0/SPICLK/SPID/SPIQ (19–24) | No-Connect — reserved for in-package flash |
| U0RXD/U0TXD (27,28) | No-Connect — unused, native USB handles programming |
| MTCK/GPIO6 (12), MTDO/GPIO7 (13), GPIO10 (16) | No-Connect — spare |

---

## Block 5 — Accelerometer (MMA8452QR1)

| Ref | Part | Value/Package | LCSC |
|---|---|---|---|
| U4 | MMA8452QR1 | QFN-16 3×3mm, 0.5mm pitch, no EP | C11360 |
| C16 | Ceramic cap | 100 nF, 0402 | C1525 |
| C17 | Ceramic cap | 100 nF, 0402 | C1525 |
| C18 | Ceramic cap | 10 µF, 0402 | C15525 |

| Pin | → |
|---|---|
| U4.14 VDD | 3V3, with C16 (100nF) + C18 (10µF) right at the pin |
| U4.1 VDDIO | 3V3 (pins 1 and 14 share a corner, so tie them together there) |
| U4.2 BYP | C17 → GND. **Internal regulator output, never connect it to 3V3** |
| U4.5, U4.10, U4.12 | GND |
| U4.4 SCL | **SCL** net |
| U4.6 SDA | **SDA** net |
| U4.7 SA0 | GND → I2C address **0x1C** (OLED is 0x3C, no clash) |
| U4.11 INT1 | **INT1** net → U3.GPIO0 (pin 4), deep-sleep wake |
| U4.9 INT2 | **INT2** net → U3.GPIO1 (pin 5), spare |
| U4.3 DNC | No-Connect flag (datasheet: leave floating) |
| U4.8, 13, 15, 16 NC | No-Connect flags |

**No resistors on INT1 or INT2.** Both pins are push-pull and always
driven, never floating. After power-on they are active-low (idle high)
until firmware sets IPOL = 1.

### Firmware setup: two shakes, one transient channel

The transient detector works on high-pass-filtered data, so gravity and
slow tilting are ignored. Wake and "next gif" use the same channel on INT1,
with firmware switching the threshold. Every config write needs the chip in
**standby** (CTRL_REG1 ACTIVE = 0), with ACTIVE = 1 written last.

| Register | Asleep: vigorous shake wakes | Awake: gentle shake = next gif |
|---|---|---|
| 0x2A CTRL_REG1 | 12.5Hz → 0x28, then 0x29 | 50Hz → 0x20, then 0x21 |
| 0x2B CTRL_REG2 | low-power mode → 0x03 (**6µA**) | 0x03 |
| 0x0E XYZ_DATA_CFG | ±8g → 0x02 | 0x02 |
| 0x0F HP_FILTER_CUTOFF | 0x00 (0.25Hz cutoff) | 0x00 (1Hz cutoff) |
| 0x1D TRANSIENT_CFG | latch + X/Y/Z, HPF on → 0x1E | 0x1E |
| 0x1F TRANSIENT_THS | 1.5g → 0x18 | 0.5g → 0x08 |
| 0x20 TRANSIENT_COUNT | 3 × 80ms → 0x03 | 2 × 20ms → 0x02 |
| 0x2C CTRL_REG3 | active-high, push-pull → 0x02 | 0x02 |
| 0x2D CTRL_REG4 | transient interrupt on → 0x20 | 0x20 |
| 0x2E CTRL_REG5 | transient → INT1 → 0x20 | 0x20 |

- **Latching:** INT1 stays high until TRANSIENT_SRC (0x1E) is read, which
  suits the ESP32-C3's level wake:
  `esp_deep_sleep_enable_gpio_wakeup(BIT(0), ESP_GPIO_WAKEUP_GPIO_HIGH)`,
  with GPIO0's internal pulls disabled.
- **On wake:** read 0x1E. Wait ~0.5–1s after the last event (the wake
  shake, plus high-pass filter settling for thresholds below 1g, see NXP
  AN4071). Then load the gentle settings.
- **Before sleep:** load the wake settings, read 0x1E, then deep sleep.
- 1.5g / 0.5g and the counts are starting points. Tune them on the bench so
  walking doesn't wake the fob.
- WHO_AM_I (0x0D) reads 0x2A.

---

## Block 6 — I2C bus

| Ref | Value |
|---|---|
| R11 | 4.7 kΩ, 0402 C25900 |
| R12 | 4.7 kΩ, 0402 C25900 |

GPIO4/GPIO5 chosen for SDA/SCL (firmware config, not fixed silicon —
whatever you pick here, firmware must match).

| Pin | → |
|---|---|
| U3.pin9 (GPIO4) | **SDA**: R11 → 3V3 · U4.pin6 · TP4 |
| U3.pin10 (GPIO5) | **SCL**: R12 → 3V3 · U4.pin4 · TP3 |

---

## Block 7 — Off-board pads

| Ref | Part |
|---|---|
| TP1–TP4 | 4× bare pad, KiCad `TestPoint` lib |
| TP5–TP6 | 2× bare pad, KiCad `TestPoint` lib |

| Pad | → | Footprint |
|---|---|---|
| TP1 | GND | `TestPoint_Pad_1.5x1.5mm` |
| TP2 | 3V3 | `TestPoint_Pad_1.5x1.5mm` |
| TP3 | SCL | `TestPoint_Pad_1.5x1.5mm` |
| TP4 | SDA | `TestPoint_Pad_1.5x1.5mm` |
| TP5 | BAT (+) | `TestPoint_Pad_2.0x2.0mm` — carries charge current |
| TP6 | GND | `TestPoint_Pad_2.0x2.0mm` |

**Change the footprints.** All six are currently
`TestPoint_Pad_1.0x1.0mm`. That's too small to hand-solder a wire reliably,
and a keychain gets yanked. A 1mm pad lifts off the board the first time a
lead gets tugged. Also put a dab of hot glue or UV glue over the battery
and OLED leads as strain relief. That costs nothing and is the single
biggest robustness gain for a pocket device.

**OLED sleep current is not in the budget, so measure it.** Before deep
sleep, send the SSD1306 `0xAE` (display off) and `0x8D, 0x10` (charge pump
off) commands. **Don't** power-gate the OLED's 3V3: SDA/SCL are pulled up
to 3V3 on this board, so an unpowered OLED gets back-powered through its
I2C pins. Most 0.96" modules also carry their own small LDO and pull-ups,
so their sleep current varies by supplier. Measure yours before trusting
any battery-life number.

No connectors here — OLED and battery both arrive as bare leads from your
sources, nothing to plug in. Label every pad on silkscreen (no housing/key
to prevent a wrong wire). Verify OLED pin order against your specific module
(varies by supplier) and battery polarity against your specific pack before
soldering — both are real "confirm yourself" items, not assumed here.

---

## Not on this board

- No battery protection IC — assumes the cell has its own. Confirm.
- No physical power switch — deliberate, see README sleep-budget math.
- No 32.768kHz RTC crystal — GPIO0/GPIO1 reused as plain RTC-IO instead.

## Component count check

**56 parts** (R10 removed with the accelerometer change).

| Group | Refs | Count |
|---|---|---|
| ICs | U1–U4, D1 (USBLC6) | 5 |
| Diode / FET | D2 (1N4148WS), Q1 (AO3401A) | 2 |
| LED | LED1 | 1 |
| Resistors | R1–R9, R11–R16 | 15 |
| Capacitors | C1–C21 | 21 |
| Inductor | L3 (RF match only) | 1 |
| Crystal / antenna | X1, AE1 | 2 |
| Switches | SW1, SW2 | 2 |
| USB-C | USBC1 | 1 |
| Pads | TP1–TP6 | 6 |

All 10k resistors (R7, R8, R9, R13, R14) use **C25744** (Basic, 1%), not
C25531 (Extended, 5%).

**Sleep budget** (battery powered, everything asleep):

| Item | µA | Source |
|---|---|---|
| ESP32-C3 deep sleep | 5 | datasheet Table 5-9 |
| MMA8452Q, low-power mode, 12.5Hz | 6 | NXP datasheet Table 3 |
| XC6206 Iq | 1 | Torex |
| MCP73831 VBAT reverse leakage | 0.25 | datasheet |
| D2 leakage (1N4148WS @ 4V) | ~0.01 | was ~7 with 1N5819WS |
| Q1, R13 | 0 | VBUS = 0V |
| Battery divider R15+R16 | 2.1 | 4.2V / 2MΩ |
| **Board total** | **~14.4** | + OLED (measure) |

The cell costs something too: its protection PCB (DW01-class) draws ~3µA,
and LiPo self-discharge is ~1–2%/month (~4–8µA equivalent on 300mAh).
**Realistic standby: ~1–1.5 years**, less whatever the OLED draws. Real
life is dominated by how often it gets shaken, not by sleep current.

Run this after placing, before wiring — if what's on the canvas doesn't
roughly match, something's missing or extra.

---

## Reference — library import (already done)

9 LCSC parts imported into `ESP32_C3_FOB/libs/lcsc/` (symbol + footprint +
3D model each), registered in `sym-lib-table`/`fp-lib-table`. Reload
libraries if your editor was already open when this happened.

| Part | KiCad symbol name | KiCad footprint name |
|---|---|---|
| MCP73831T-2ACI/OT | `MCP73831T-2ACI{slash}OT` | `C424093_SOT-23-5_L3_0-W1_7-P0_95-LS2_8-BL` |
| XC6206P332MR | `XC6206P332MR` | `C5446_SOT-23-3_L2_9-W1_6-P1_90-LS2_8-BR` |
| ESP32-C3FH4 | `ESP32-C3FH4` | `C2858491_QFN-32_L5_0-W5_0-P0_50-TL-EP3_7` |
| MMA8452QR1 | import C11360 with the LCSC plugin | as generated by the import |
| USBLC6-2SC6 | `USBLC6-2SC6` | `C7519_SOT-23-6_L2_9-W1_6-P0_95-LS2_8-BL` |
| Crystal 40MHz | `3225_40M_12PF_10PPM` | `C5380316_CRYSTAL-SMD_4P-L3_2-W2_5-BL` |
| Johanson antenna | `Mini_2_45_GHz_Antenna,_Johanson_Technology` | `C89334_ANT-SMD_L3_2-W1_6` |
| Tactile switch | `TS342A2P` | `C398055_SW-SMD_L4_0-W3_0-LS5_0-EH` |
| USB-C receptacle | `TYPE-C-31-M-12` | `C165948_USB-C_SMD-TYPE-C-31-M-12_1` |

Note: C13738 (originally picked for the crystal) was a 16MHz part, wrong —
swapped for C5380316 (40MHz, confirmed), deleted from the library rather
than left in. S2B-PH-SM4-TB / C295747 (battery connector) was also
imported, then dropped — board uses solder pads instead (Block 7).

Generic parts (KiCad built-in `Device`/`TestPoint` libs, no import): all R/C/L,
D1, TP1–6.

**Packages:** every passive is **0402**. JLC Economic PCBA's minimum is
0402, and a single 0201 forces Standard PCBA (≥70×70mm board or a railed
panel, plus a higher fee). The earlier 0201 plan was dropped for that reason.

## Reference — verified against Espressif's live checklist

Checked every value in this document against
[docs.espressif.com's schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html)
directly — all matched except the crystal load-cap formula (PDF extraction
had garbled it; corrected: `C_L=(C1×C2)/(C1+C2)+C_stray` → C1=C2=18pF). One
item on their checklist not here: 499Ω on U0TXD — skipped, UART0 unused.
