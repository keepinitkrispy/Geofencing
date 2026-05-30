# The Dome VB — grandMA3 FX Recipe Library

## Venue Layout

**The Dome by Rutter Mills** — Virginia Beach, VA (Oceanfront district)
Multi-level indoor concert hall with proscenium stage, general admission floor,
and tiered/VIP areas. Outdoor Lawn Plaza for overflow.

**Rig positions:**
- **FOH truss** — back of room, over audience, shooting toward stage
- **Mid-room truss** — over the floor, midway between FOH and stage
- **Back truss / upstage** — over or behind the stage, backlight and top-wash
- **Proscenium** — arch framing the stage opening, DMX LED strips on both sides

---

## Programming Philosophy for This Rig

The primary creative axis is **depth: FOH → Mid → Stage**. Effects that travel
along this axis feel like they pass through the room and land on the performers —
or launch off the stage and hit the audience.

**Three keys to this rig:**

1. **Group by position depth** — FOH, Mid, Stage. Phase fans across depth create
   waves that travel through the room. This is your most powerful axis.
2. **Use the proscenium strips as a frame** — they define where the stage begins.
   They can pulse with the music, trace an outline, or react to the show independently.
3. **Left/right symmetry vs. asymmetry** — symmetric looks feel polished and intentional;
   breaking symmetry (different phases or colors L vs. R) creates tension and drama.

---

## How to Read These Recipes

| Field | Meaning |
|-------|--------|
| **Attribute** | The fixture parameter the FX runs on |
| **Waveform** | Sine / Cosine / Square / Ramp Up / Ramp Down / Random |
| **Speed** | Hz — 1 Hz = 60 BPM, 2 Hz = 120 BPM |
| **Size** | Amplitude as % of attribute range, or degrees for position |
| **Phase Spread** | Total phase difference across the group — Fan across depth or width |
| **Sort** | How to order fixtures when fanning phase |

BPM reference: 120 BPM = 2 Hz · 60 BPM = 1 Hz · 30 BPM = 0.5 Hz

---

## DJ / Club Night Recipes

### 1. Room Pulse — Depth Wave
*Energy appears to launch from the stage and wash over the audience, or reverse.*

**Groups:** Back/stage fixtures, Mid-room fixtures, FOH fixtures — in that order.

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Sort |
|-------|-----------|----------|-------|------|--------------|------|
| 1 | Dimmer | Sine | 2 Hz | 70% | Stage=0° → Mid=120° → FOH=240° | Depth, stage to FOH |
| 2 | Color Temp | Sine | 0.3 Hz | 20% | 0° (all together) | — |

**Direction:** Reverse phase order (FOH=0° → Stage=240°) and the pulse travels
from audience toward the stage instead — great for builds.

**MA3 tip:** Rate master this. At 1x it tracks 120 BPM. Push to 2x for 240 BPM intensity.

---

### 2. Aerial Beam Storm
*Spots on all truss positions sweep simultaneously — creates layered aerial chaos that feels musical.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Sort |
|-------|-----------|----------|-------|------|--------------|------|
| 1 | Pan | Sine | 0.5 Hz | 65° | 0°→180° | Left to right across each truss |
| 2 | Tilt | Cosine | 0.5 Hz | 40° | 90° offset from Pan | Same sort |
| 3 | Dimmer | Sine | 1 Hz | 45% | 0°→270° | FOH to Stage depth |

Set Tilt waveform to Cosine (90° offset from Pan's Sine) — this creates oval/orbital
beam paths in the air rather than a flat side-to-side sweep. With three truss positions
at different depths, beams cross each other constantly.

---

### 3. Hue Chase — FOH to Stage
*A color wave rolls from the back of the room to the stage and repeats.*

**Works on:** All wash + LED strips

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Sort |
|-------|-----------|----------|-------|------|--------------|------|
| 1 | Hue | Ramp Up | 0.2 Hz | 360° | 0°→360° | FOH to Stage (depth sort) |
| 2 | Dimmer | Sine | 0.5 Hz | 30% | Matches Hue spread | Same sort |

In MA3: Select all wash → Fan → Sort "By Position (Y axis)" if stage is on Y axis of
your layout. This ties phase to physical depth, so the color wave actually travels
through the room.

---

### 4. Pan Pendulum — Symmetric Split
*Left and right halves of the rig swing in opposite directions — X-cross aerial effect.*

Split every truss into Left group and Right group.

| Group | Attribute | Waveform | Speed | Size | Phase | Notes |
|-------|-----------|----------|-------|------|-------|-------|
| Left spots | Pan | Sine | 0.5 Hz | 55° | 0° | Swings stage-left |
| Right spots | Pan | Sine | 0.5 Hz | 55° | 180° | Opposite — swings stage-right |
| All spots | Tilt | Sine | 0.25 Hz | 15° | 0° | Shared slow tilt keeps beams aerial |

Add phase spread within each half-group (0°→90°) so it's not a single hard arm but
a soft fan of beams crossing.

---

### 5. Strobe Depth Chase
*Blinders/strobes fire from stage outward to FOH in sequence — feels like an explosion expanding.*

Build as a **sequence chase** (not FX engine):

| Step | Fixtures | Dimmer | Frame Time |
|------|----------|--------|------------|
| 1 | Back/stage blinders | 100% | 2 frames |
| 2 | Mid-room blinders | 100% | 2 frames |
| 3 | FOH blinders | 100% | 2 frames |
| 4 | All out | 0% | 3 frames |

Run slow (30 BPM) for buildup, accelerate into the drop. At the peak: switch to a
full-rig Strobe FX (Square wave, 8–12 Hz, 100% size) triggered on a separate executor.

---

### 6. Bass Drop Punch
*One-shot cue for drops — full rig hits hard, then decays with a fast dimmer pulse.*

Program as a dedicated executor, triggered manually:

- **Cue 1 (0 fade):** All fixtures → Dimmer 100%, Zoom fully open (wash), Iris open (spot)
- **Cue 2 (auto-follow, 0.1s):** FX layer — Dimmer Sine, 3 Hz, 55% size, 0 phase, all fixtures
- **Cue 3 (auto-follow, 3s fade):** FX removed, return to base look

Use sparingly. One per section, not every 16 bars.

---

## Concert / Band Recipes

### 7. Breathing Room
*The whole rig gently pulses — alive without competing with the performance.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer (all) | Sine | 0.3 Hz | 25% | 0° (no fan) | Room breathes as one organism |
| 2 | Tilt (spots) | Sine | 0.12 Hz | 6° | 0°→30° depth | Barely perceptible drift |

Keep intensity anchored at 60–70%. FX rides on top — it should feel like the room
is breathing, not flickering.

---

### 8. Depth Tilt Wave
*A wave of beam direction travels from FOH to stage — like a wave rolling onto shore.*

**Groups:** Sort spots by depth position (FOH = first, Stage = last).

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Tilt | Sine | 0.4 Hz | 35° | FOH=0° → Stage=180° | Wave moves stage-direction |
| 2 | Dimmer | Sine | 0.4 Hz | 30% | Matches Tilt spread | Intensity follows the wave |

---

### 9. Proscenium Frame Pulse
*The LED strips on either side of the proscenium become a reactive frame around the stage.*

**Fixtures:** Proscenium DMX LED strips (left side + right side)

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Sine | 0.5 Hz | 40% | Bottom=0° → Top=180° (fan vertically) | Pulse traces the arch upward |
| 2 | Hue | Sine | 0.15 Hz | 30° | 0° (both sides together) | Color breathes with show |

**Variant — Mirror trace:** Fan bottom→top on left strip, top→bottom on right strip.
The pulse appears to trace up one side and down the other, meeting at the top of the arch.

---

### 10. Gobo Texture Layer
*Projected patterns breathe and shift — adds depth to a static color look.*

**On:** Spots with rotating gobos (any truss position)

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Gobo Rotation | Ramp Up | 0.4 Hz | 100% | FOH spots CW, Stage spots CCW | Counter-rotation at different depths |
| 2 | Dimmer | Sine | 0.6 Hz | 45% | 0°→180° depth sort | Projection pulses travel room |
| 3 | Focus | Sine | 0.15 Hz | 20% | 0° | Sharpness breathes slowly |

---

### 11. Color Zone Chase — Stage Areas
*Color identity moves across stage zones left to right, then resets.*

Build as a **sequence** with 3 steps, each a stage zone:

- Step 1: Stage-left wash — Band color A (8-beat crossfade)
- Step 2: Center wash — Band color B (8-beat crossfade)
- Step 3: Stage-right wash — Band color A or C (8-beat crossfade)

Simultaneously: Dimmer Sine FX (0.4 Hz, 20% size, 0 phase) over all wash — each zone
pulses independently within its color. Loop runs continuously under the show.

---

### 12. Key Light Heartbeat
*Front wash on performers breathes subtly — keeps energy without losing visibility.*

**Fixtures:** FOH spots/wash (front key positions only)

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Sine | Music BPM ÷ 4 | 15% | 0° | All key fixtures together |

Size at 15% means intensity only moves between ~55% and ~70% — performers stay lit,
but the look has pulse. Scale up to 25% size for more drama, back to 10% for subtle.

---

## Corporate / Ambient Recipes

### 13. Architectural Slow Wash
*Proscenium strips and wash create a soft, living environment — suitable for cocktail hour, reception.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer (wash) | Sine | 0.15 Hz | 18% | 0° | All wash together, very gentle |
| 2 | Hue (wash) | Sine | 0.05 Hz | 20° | 0° | Slow color drift, stays in brand range |
| 3 | Dimmer (proscenium) | Sine | 0.1 Hz | 12% | Bottom→Top | Strips slowly breathe |

Intensity anchored at 50%. Color centered on brand palette. Nothing moves fast.

---

### 14. Brand Presence Look
*Full room in brand colors, barely alive — polished and controlled.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer (all) | Sine | 0.18 Hz | 12% | 0° | Barely perceptible room pulse |
| 2 | Tilt (spots) | Sine | 0.08 Hz | 4° | 0°→20° depth | Near-invisible drift |

Color and position locked in presets. FX runs underneath — the only goal is that
the room doesn't look frozen on a photograph.

---

### 15. Clean Aerial Lines
*Spots hold gentle slow sweeps — creates interest overhead without distracting from speakers or presenters.*

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Pan | Sine | 0.07 Hz | 20° | 0°→120° left-to-right | Very slow fan |
| 2 | Tilt | Sine | 0.05 Hz | 10° | 90° offset | Different period = organic |

Intensity at 25–35%. No color FX. No strobe.

---

## Signature Moves (Venue-Specific)

### 16. Room Wave — Full Depth
*The entire rig fires from back to front — the pulse travels through the whole room.*

All fixtures, sorted by depth (FOH first, Stage last):

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Sine | 1 Hz | 75% | FOH=0° → Stage=270° | Pulse travels FOH→Stage |
| 2 | Tilt | Sine | 1 Hz | 25° | Matches Dimmer spread | Beams tilt with the pulse |
| 3 | Hue | Ramp Up | 0.25 Hz | 360° | 0° (all together) | Color rolls continuously underneath |

This is the "everything" move. Run at key moments — not every chorus.

---

### 17. Proscenium to Rig Cascade
*Color or intensity starts at the proscenium frame and cascades outward to fill the room.*

Triggerable sequence (one-shot):

| Step | Fixtures | Action | Fade |
|------|----------|--------|------|
| 1 | Proscenium strips | Dimmer 100%, color spike | 0s in, 1.5s out |
| 2 | Back/stage wash | Color + dimmer up | 0.3s delay, 0.8s fade |
| 3 | Mid wash | Same | 0.3s delay, 0.8s fade |
| 4 | FOH wash | Same | 0.3s delay, 0.8s fade |
| 5 | All return | Base look | 2s fade |

Use for walk-ons, reveal moments, first song of a set.

---

### 18. L/R Asymmetric Break
*Breaking the room's natural symmetry to create tension — useful in builds before a release.*

Split rig into Stage-Left and Stage-Right groups.

| Group | Attribute | Waveform | Speed | Size | Phase | Color |
|-------|-----------|----------|-------|------|-------|-------|
| Stage Left | Pan | Sine | 0.6 Hz | 50° | 0° | Color A |
| Stage Right | Pan | Sine | 0.9 Hz | 50° | 45° | Color B |
| All | Dimmer | Sine | 0.4 Hz | 30% | 0° | — |

The different speeds (0.6 vs 0.9 Hz) mean the two halves drift in and out of sync —
creates natural tension that resolves when you snap back to a symmetric look at the drop.

---

### 19. Proscenium VU Meter
*Strips react like a VU meter during high-energy moments — vertical chase tied to music.*

**Fixtures:** Proscenium LED strips, fanned pixel-by-pixel from bottom to top.

| Layer | Attribute | Waveform | Speed | Size | Phase Spread | Notes |
|-------|-----------|----------|-------|------|--------------|-------|
| 1 | Dimmer | Ramp Up | 1–2 Hz | 100% | Bottom pixel=0° → Top=360° | Chase runs bottom to top |
| 2 | Hue | Step (via sequence) | Matched | — | — | Color changes per energy level |

If strips are pixel-mappable in MA3: use the Pixel Mapper to drive a simple vertical
gradient that responds to a Rate Master fader. Push fader = higher the "fill" reads.

---

## Rate Master Strategy

One Rate Master executor governs all looping FX sequences:

| Fader % | Rate | Use Case |
|---------|------|----------|
| 0% | Frozen | Hold as static scene |
| 25% | 0.5x | Ballads, slow builds, ambient |
| 50% | 1x | Default energy level |
| 75% | 1.5x | Rising energy, second half of show |
| 100% | 2x | Peak intensity, drops |

---

## Waveform Reference

| Waveform | Best For |
|----------|---------|
| Sine | Smooth organic movement — position sweeps, dimmer breathing |
| Cosine | Same as Sine but starts at peak — use for 90° phase tricks (orbital beams) |
| Ramp Up | Continuous rotation, color wheel chase, one-direction travel |
| Ramp Down | Reverse chase direction |
| Square | Hard on/off strobing, mechanical chase feel |
| Random | Fire, organic atmosphere, haze/fog movement simulation |

---

## What's Next

- **Color palette library** — MA3 color presets for DJ, concert, and corporate
- **Cue stack templates** — executor page layouts per event type
- **Lua plugin** — auto-generates depth-sorted groups and phase fans from fixture layout
- **Look library** — full scenes (color + position + beam + FX stacked) per event type
- **House patch** — ready to build once patch list is in hand

---

*Rig: Spots, Wash, Blinders/Strobes/Pixel, Proscenium LED Strips*
*FOH truss · Mid-room truss · Back/upstage truss · Proscenium arch*
*The Dome by Rutter Mills — Virginia Beach, VA*
*Platform: grandMA3*
