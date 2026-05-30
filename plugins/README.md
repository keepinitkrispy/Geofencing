# FCHS Prom 2026 — grandMA3 Plugins

## Install
Copy all `.lua` files to:
```
[MA3 root]/shared/resource/lib/plugins/
```
Windows: `C:\ProgramData\MALightingTechnology\gma3\[version]\shared\resource\lib\plugins\`

## Run Order

| Step | Plugin | Command | When |
|------|--------|---------|------|
| 1 | `prom_color_presets.lua` | `Plugin "prom_color_presets"` | After patching |
| 2 | `prom_groups.lua` | `Plugin "prom_groups"` | After patching |
| 3 | `prom_fx_sequences.lua` | `Plugin "prom_fx_sequences"` | After step 2 |
| 4 | `prom_cuelist.lua` | `Plugin "prom_cuelist"` | After step 3 |

## What Each Plugin Creates

### prom_color_presets.lua
7 color presets — Pool 4 slots 101–107: Patriot Blue, Patriot Gold, Soft Gold, Deep Blue, Champagne, Lavender, White

### prom_groups.lua
13 named groups (101–113). Interactive — you select fixtures for each group when prompted.

### prom_fx_sequences.lua
8 looping FX sequences (801–808). Assign to executor faders on Page 1.

### prom_cuelist.lua
Sequence 900 — full show with 17 named cues. Structure only, program content into each cue.

## Notes
- Written for grandMA3 v1.9+
- FX command syntax (`FX Add`) — if it doesn't store, check the command line echo and adjust
- Rate Master: assign a fader to control Rate for sequences 801–808 live
