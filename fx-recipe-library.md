# The Dome VB — grandMA3 FX Recipe Library

## Dome Programming Philosophy

The dome's geometry is your biggest creative advantage. Fixtures arranged in concentric
rings or radiating spokes let you create effects that feel impossible in a flat room:
pulses that bloom outward from center, rotational sweeps like a lighthouse, and waves
that ripple from the rig down to the audience.

**Three keys to dome FX:**

1. **Group by ring/radius** — not by universe or fixture number. Inner ring, mid ring,
   outer ring each get their own group. This is how you build concentric FX.
2. **Phase = position** — use Fan to spread phase across fixture groups based on their
   physical position in the dome. The FX engine turns position into time offset.
3. **Stack attributes** — a single look runs FX on dimmer, color, AND tilt simultaneously
   at different speeds. Each layer adds depth without complexity.

---

## How to Read These Recipes

Each recipe lists MA3 FX parameters:

| Field | Meaning |
|-------|--------|
| **Attribute** | The fixture parameter the FX runs on |
| **Waveform** | Sine / Cosine / Square / Ramp Up / Ramp Down / Random |
| **Speed** | Hz (cycles per second) — 1 Hz = 60 BPM |
| **Size** | Amplitude as % of attribute range, or degrees for position |
| **Phase Spread** | Total phase difference across the group (Fan this across fixtures) |
| **Offset** | Global phase shift (delays the whole group) |

BPM reference: 120 BPM = 2 Hz, 60 BPM = 1 Hz, 30 BPM = 0.5 Hz

---

## DJ / Club Night Recipes

### 1. Centripetal Dimmer Pulse
*The dome appears to breathe inward — energy rushes from edges toward center on every beat.*

**Setup:** Group fixtures by ring. Outer ring = Group 1, Mid = Group 2, Inner = Group 3.

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Sine | 2 Hz (120 BPM) | 70% | 0° outer → 270° inner | Fan across ring groups |
| 2 | Color Temp / Tint | Sine | 0.25 Hz | 20% | 0° | Subtle warmth pulse, all together |

**MA3 tip:** Rate master this at 50%–200% so the LD can chase tempo live without
reprogramming.

---

### 2. Aerial Beam Storm
*Spots fill the dome with sweeping aerial beams that feel alive and chaotic but stay musical.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Pan | Sine | 0.4 Hz | 70° | 0°→240° (fan across all spots) | Primary sweep |
| 2 | Tilt | Cosine | 0.4 Hz | 45° | 90° offset from layer 1 | Offset makes it orbital not linear |
| 3 | Dimmer | Sine | 0.8 Hz | 40% | 0°→360° | Beams pulse individually |

**Note:** Set Tilt FX offset to 90° relative to Pan — this creates circular/orbital beam
paths rather than a flat linear sweep. The dome catches all of it.

---

### 3. Hue Rotation Wave
*A continuous wave of color rolls across the entire rig, never stopping.*

**Works on:** Wash + LED strips

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Hue | Ramp Up | 0.15 Hz | 360° | 0°→360° (fan all fixtures by position) | Continuous color wheel |
| 2 | Dimmer | Sine | 0.5 Hz | 25% | Matches hue fan direction | Adds depth to the wave |

**MA3 tip:** Use "Sort by Position" when fanning so the wave travels physically across
the rig rather than jumping by fixture number.

---

### 4. Strobe Grid Chase
*Blinders / pixels fire in a sequence that radiates outward — feels like the room is exploding.*

This is a **sequence-based** recipe, not FX engine. Build a chase in a separate sequence:

- Step 1: Inner ring blinders (2 frames)
- Step 2: Mid ring (2 frames)  
- Step 3: Outer ring (2 frames)
- Step 4: All blackout (2 frames)

Run at 8–16 BPM for buildup, ramp up speed into a drop.
Layer a Strobe FX (Square wave, 8 Hz, 100% size) on all blinders simultaneously for the
drop itself.

---

### 5. Pan Pendulum Cross
*Two halves of the spot rig swing in opposite directions — creates dramatic aerial X-crossings.*

Split spots into Left Half and Right Half groups.

| Group | Attribute | Waveform | Speed | Size | Phase | Notes |
|-------|-----------|----------|-------|------|-------|-------|
| Left half | Pan | Sine | 0.5 Hz | 60° | 0° | Swings left→right |
| Right half | Pan | Sine | 0.5 Hz | 60° | 180° | Opposite phase — swings right→left |
| Both | Tilt | Sine | 0.25 Hz | 20° | 0° | Slow shared tilt keeps beams in air |

---

### 6. Bass Drop Bloom
*Single triggerable moment — everything explodes outward from dome center then recovers.*

This is a **one-shot cue**, not a looping FX. Program as Cue 1 on a dedicated executor:

- **Beat:** All fixtures, Dimmer 100%, Zoom open (wash), Iris open (spot) — 0 fade
- **Tail:** FX on Dimmer (Sine, 3 Hz, 60% size, 0 phase, 0 delay) — runs for 4 beats
- **Recovery:** Follow cue fades back to base look over 2 seconds

Trigger manually on drops. Keep it rare — the dome makes this hit hard.

---

## Concert / Band Recipes

### 7. Breathing Wash
*The rig stays alive between musical moments without pulling focus.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Sine | 0.3 Hz | 30% | 0° (all together) | No fan — room breathes as one |
| 2 | Tilt | Sine | 0.15 Hz | 8° | 0°→45° | Barely perceptible movement |

Keep Size small. The goal is "alive" not "active." Color stays in presets.

---

### 8. Tilt Wave — Floor to Dome
*A wave of beam direction rolls from audience level up through the dome.*

**Setup:** Group spots by vertical position / tilt range (low = audience, high = dome apex).

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Tilt | Sine | 0.4 Hz | 40° | 0° (low/audience) → 180° (high/dome) | Fan from floor to ceiling |
| 2 | Dimmer | Sine | 0.4 Hz | 35% | Matches tilt fan | Wave of intensity follows direction |

---

### 9. Synchronized Color Shift
*All wash fixtures slowly drift through a color range together — feels cinematic.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Hue | Sine | 0.08 Hz | 45° | 0° | Very slow, all together |
| 2 | Saturation | Sine | 0.05 Hz | 20% | 0° | Saturation breathes slightly slower |

Program the center Hue value to match the band's key color. The FX drifts around it.

---

### 10. Gobo Pulse Layer
*Projected texture breathes with the music — adds dimensionality without movement.*

**On:** Spots with rotating gobos

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Gobo Rotation | Ramp Up | 0.5 Hz | 100% | 0°→180° | Half fixtures spin CW, half CCW |
| 2 | Dimmer | Sine | 0.6 Hz | 50% | 0°→120° | Projection pulses chase across rig |
| 3 | Focus/Zoom | Sine | 0.2 Hz | 30% | 0° | Sharpness breathes slowly |

---

### 11. Stage Wash Color Chase
*Color identity travels across stage zones — guitar, keys, drums each get a wave.*

Build as a **sequence** (not FX engine) with 3–4 color steps, one per stage zone.
- Step 1: Downstage left wash (band color A) — 8 beat fade
- Step 2: Center wash (band color B) — 8 beat fade
- Step 3: Downstage right wash (band color A or C) — 8 beat fade

Layer FX: Dimmer Sine (0.5 Hz, 20% size, 0 phase) over all wash simultaneously for
pulse within each color zone.

---

## Corporate / Ambient Recipes

### 12. Architectural Trace
*LED strips following dome ribs glow softly, subtly tracing the building's structure.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Sine | 0.12 Hz | 20% | 0°→270° fan across strips | Very slow, gentle ripple |
| 2 | Color Temp | Sine | 0.06 Hz | 15% | 0° | Barely perceptible warmth shift |

Anchor intensity at 40–60%. FX rides on top. The dome structure becomes the design.

---

### 13. Brand Color Presence
*Entire room holds brand colors with a heartbeat — alive but professional.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer (wash) | Sine | 0.2 Hz | 15% | 0° | All together, subtle |
| 2 | Tilt (spots) | Sine | 0.1 Hz | 5° | 0°→30° | Near-imperceptible drift |

Color set in presets — brand palette locked in, FX just keeps it from feeling static.

---

### 14. Clean Ambient Sweep
*Spots drift slowly, creating gentle aerial lines that complement conversation.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Pan | Sine | 0.08 Hz | 25° | 0°→180° | Very slow fan sweep |
| 2 | Tilt | Sine | 0.06 Hz | 15° | 90° offset | Slightly different period feels organic |

Intensity at 30–50% for spots. No strobe. No color FX.

---

## Dome Signature Moves

*These are unique to a dome and won't read the same way in any other venue.*

### 15. Radial Bloom
*The single most identifiable dome effect — a wave opens from the center apex outward.*

**Setup:** Group all fixtures by radial distance from dome center (not stage center).
- Ring A: Fixtures closest to dome apex / center
- Ring B: Mid-dome
- Ring C: Outer perimeter

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Tilt (toward apex) | Sine | 0.5 Hz | 50° | Ring A=0°, B=90°, C=180° | Bloom wave |
| 2 | Dimmer | Sine | 0.5 Hz | 60% | Matches tilt phase | Intensity follows bloom |
| 3 | Zoom (wash) | Sine | 0.5 Hz | 40% | Matches tilt phase | Beam widens as it blooms |

**Effect:** A pulse appears to originate from the dome's highest point and radiates
downward/outward to the edges like a flower opening. Run slow (0.3 Hz) for drama,
fast (1 Hz) for energy.

---

### 16. Rotational Sweep
*One "arm" of light appears to spin around the inside of the dome like a lighthouse.*

**Setup:** Spots arranged around the dome perimeter, fanned 0°→360° by their angular
position (not fixture number). Sort by XY position on the plot.

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Pan | Ramp Up | 0.15 Hz | 40° | 0°→360° sorted by angle | The rotating arm |
| 2 | Dimmer | Sine | 0.15 Hz | 70% | Same sort, 0°→360° | Only one "arm" lit at a time |

**Key:** The Dimmer FX at matching phase is what makes it read as a single rotating arm
rather than all fixtures moving simultaneously. Use a narrow Size on dimmer (try 40%)
to get a tight "arm" effect.

---

### 17. Concentric Ring Pulse
*Ripples radiate from the center outward — like dropping a stone in still water.*

Run as a **timed sequence** for maximum control:

| Step | Fixtures | Dimmer | Fade In | Hold | Fade Out |
|------|----------|--------|---------|------|----------|
| 1 | Ring A (inner) | 100% | 0.1s | 0.2s | 0.8s |
| 2 | Ring B (mid) | 100% | 0.1s | 0.2s | 0.8s |
| 3 | Ring C (outer) | 100% | 0.1s | 0.2s | 0.8s |
| 4 | All dark | 0% | 0 | 0.5s | 0 |

Loop. Adjust speed: slow (2s/ring) for ambient, fast (0.3s/ring) for intensity.
Layer a Hue Ramp Up FX (very slow) over all rings so color shifts between pulses.

---

### 18. Dome Vortex
*Everything spirals — beams rotate, colors chase, the entire room feels like it's spinning.*

This stacks three FX running simultaneously:

| Layer | Fixtures | Attribute | Waveform | Speed | Size | Phase | Notes |
|-------|----------|-----------|----------|-------|------|-------|-------|
| 1 | All spots | Pan | Ramp Up | 0.2 Hz | 60° | 0°→360° by angle position | The spin |
| 2 | All wash | Hue | Ramp Up | 0.3 Hz | 360° | 0°→360° by angle position | Color chases the spin |
| 3 | LED strips | Dimmer | Sine | 0.6 Hz | 80% | 0°→360° by dome position | Structural highlights orbit |

**Phase sort method in MA3:** Select all fixtures → Attribute → Fan → Sort "By Position"
(use the fixture layout grid). This ensures phase is tied to physical location,
not fixture ID.

---

## Rate Master Strategy

Set up a Rate Master executor for each recipe category:

| Fader Position | Rate | Use Case |
|----------------|------|----------|
| 0% | 0 (frozen) | Hold a look as a static scene |
| 25% | 0.5x | Ballads, slow builds, ambient |
| 50% | 1x (default) | Standard energy |
| 75% | 1.5x | Building energy |
| 100% | 2x | Peak / drop moments |

All FX sequences should reference the same Rate Master so one fader controls the
feel of the entire show.

---

## Quick Reference: Waveform Cheat Sheet

| Waveform | Best For |
|----------|---------|
| Sine | Smooth, organic movement — position, dimmer breathing |
| Cosine | Same as Sine but starts at peak — use for phase offset tricks |
| Ramp Up | Continuous rotation, color wheel chases, orbital motion |
| Ramp Down | Reverse chases |
| Square | Strobing, hard on/off chases, mechanical feel |
| Random | Fire, organic chaos, atmospheric haze movement |

---

## Next Steps

- **Cue stack templates** — pre-built executor layouts for each event type
- **Color palette library** — presets for DJ/concert/corporate with MA3 color coordinates
- **Lua plugin** — auto-generates ring groups and phase fans from fixture layout data
- **Look library** — full scenes (color + position + beam + FX) ready to program

---

*Rig: Spots, Wash, Blinders/Strobes/Pixel, LED Strips — The Dome, Virginia Beach*
*Platform: grandMA3 — Branch: claude/grandma3-fx-cues-looks-894AY*
