-- ================================================================
-- prom_fx_sequences.lua
-- FCHS Prom 2026 — Build FX executor sequences (801-808)
-- ================================================================
-- INSTALL: Copy to [MA3 root]/shared/resource/lib/plugins/
-- RUN:     Plugin "prom_fx_sequences"
-- WHEN:    Run AFTER prom_groups.lua — requires groups 101-113
-- RESULT:  8 looping FX sequences. Assign to executor faders.
-- ================================================================
-- 801  Room Pulse         depth wave, all wash
-- 802  Aerial Beam Storm  all spots, orbital pan+tilt
-- 803  Hue Chase          color wave FOH→Stage
-- 804  Pan Pendulum Cross spots left/right split
-- 805  Strobe Depth Chase blinders stage→FOH sequence
-- 806  Pros Frame Pulse   proscenium strips
-- 807  Breathing Room     slow ambient, all fixtures
-- 808  Slow Dance Breathe very slow, romantic
-- ================================================================

local SEQ_BASE = 800

local function makeSeq(number, name)
    gma.cmd(string.format('Delete Sequence %d /nc', number))
    gma.sleep(50)
    gma.cmd(string.format('Store Sequence %d "%s" /nc', number, name))
    gma.sleep(100)
    gma.echo(string.format("  Created sequence %d: %s", number, name))
end

local function run()

    if not gma.gui.confirm("FCHS Prom — FX Sequences",
        "Build 8 FX executor sequences (801-808)?\n\n" ..
        "Requires groups 101-113 from prom_groups.lua.\n" ..
        "Existing sequences 801-808 will be deleted and rebuilt.") then
        return
    end

    gma.echo("=== FCHS Prom: building FX sequences ===")

    -- 801: ROOM PULSE — depth wave across wash
    makeSeq(801, "Prom-FX RoomPulse")
    gma.cmd("Group 106") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 80') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 2 Size 70 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 801.1 "Room Pulse" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd("Group 105") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 80') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 2 Size 70 Phase 90') gma.sleep(40)
    gma.cmd('Store Cue 801.1 "Room Pulse" /nc /merge') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd("Group 104") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 80') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 2 Size 70 Phase 180') gma.sleep(40)
    gma.cmd('Store Cue 801.1 "Room Pulse" /nc /merge') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 801.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 801: Room Pulse")

    -- 802: AERIAL BEAM STORM — orbital pan+tilt, all spots
    makeSeq(802, "Prom-FX BeamStorm")
    gma.cmd("Group 111") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 85') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Pan" Rate 0.5 Size 65') gma.sleep(40)
    gma.cmd('FX Add "Cosine" Attribute "Tilt" Rate 0.5 Size 40') gma.sleep(40)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 1 Size 45 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 802.1 "Beam Storm" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 802.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 802: Aerial Beam Storm")

    -- 803: HUE CHASE — color wave FOH→Stage
    makeSeq(803, "Prom-FX HueChase")
    gma.cmd("Group 104") gma.sleep(50)
    gma.cmd('FX Add "RampUp" Attribute "Hue" Rate 0.2 Size 100 Phase 0') gma.sleep(40)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.5 Size 30 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 803.1 "Hue Chase" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd("Group 105") gma.sleep(50)
    gma.cmd('FX Add "RampUp" Attribute "Hue" Rate 0.2 Size 100 Phase 120') gma.sleep(40)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.5 Size 30 Phase 120') gma.sleep(40)
    gma.cmd('Store Cue 803.1 "Hue Chase" /nc /merge') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd("Group 106") gma.sleep(50)
    gma.cmd('FX Add "RampUp" Attribute "Hue" Rate 0.2 Size 100 Phase 240') gma.sleep(40)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.5 Size 30 Phase 240') gma.sleep(40)
    gma.cmd('Store Cue 803.1 "Hue Chase" /nc /merge') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 803.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 803: Hue Chase FOH→Stage")

    -- 804: PAN PENDULUM CROSS — all spots, fanned 180-degree phase
    makeSeq(804, "Prom-FX PanPendulum")
    gma.cmd("Group 111") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 85') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Pan" Rate 0.5 Size 55 Phase 0') gma.sleep(40)
    gma.cmd('FX Add "Sine" Attribute "Tilt" Rate 0.25 Size 15 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 804.1 "Pan Pendulum" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 804.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 804: Pan Pendulum Cross")

    -- 805: STROBE DEPTH CHASE — blinders stage outward
    makeSeq(805, "Prom-FX StrobeChase")
    for step = 1, 3 do
        gma.cmd("Group 109") gma.sleep(50)
        gma.cmd('Attribute "Dimmer" At 100') gma.sleep(30)
        gma.cmd('Attribute "Shutter" At 100') gma.sleep(30)
        gma.cmd(string.format('Store Cue 805.%d "Blinder Step %d" /nc', step, step)) gma.sleep(150)
        gma.cmd("Clear") gma.sleep(50)
    end
    gma.cmd("Group 109") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 0') gma.sleep(30)
    gma.cmd('Store Cue 805.4 "Blinder Out" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    for step = 1, 4 do
        gma.cmd(string.format('Cue 805.%d Property "InFade" 0', step)) gma.sleep(30)
        gma.cmd(string.format('Cue 805.%d Property "OutFade" 0', step)) gma.sleep(30)
        gma.cmd(string.format('Cue 805.%d Property "Trigger" "Follow"', step)) gma.sleep(30)
        gma.cmd(string.format('Cue 805.%d Property "FollowDelay" 0.1', step)) gma.sleep(30)
    end
    gma.cmd('Cue 805.4 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 805: Strobe Depth Chase")

    -- 806: PROSCENIUM FRAME PULSE
    makeSeq(806, "Prom-FX ProsPulse")
    gma.cmd("Group 113") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 70') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.5 Size 40 Phase 0') gma.sleep(40)
    gma.cmd('FX Add "Sine" Attribute "Hue" Rate 0.15 Size 30 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 806.1 "Pros Pulse" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 806.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 806: Proscenium Frame Pulse")

    -- 807: BREATHING ROOM — slow ambient
    makeSeq(807, "Prom-FX Breathe")
    gma.cmd("Group 112") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 65') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.3 Size 25 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 807.1 "Breathe" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd("Group 111") gma.sleep(50)
    gma.cmd('FX Add "Sine" Attribute "Tilt" Rate 0.12 Size 6 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 807.1 "Breathe" /nc /merge') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 807.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 807: Breathing Room")

    -- 808: SLOW DANCE BREATHE — very slow, romantic
    makeSeq(808, "Prom-FX SlowDance")
    gma.cmd("Group 112") gma.sleep(50)
    gma.cmd('Attribute "Dimmer" At 60') gma.sleep(30)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.2 Size 20 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 808.1 "Slow Dance" /nc') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd("Group 104") gma.sleep(50)
    gma.cmd('FX Add "Sine" Attribute "Dimmer" Rate 0.15 Size 10 Phase 0') gma.sleep(40)
    gma.cmd('Store Cue 808.1 "Slow Dance" /nc /merge') gma.sleep(150)
    gma.cmd("Clear") gma.sleep(50)
    gma.cmd('Cue 808.1 Property "Loop" "Loop"') gma.sleep(50)
    gma.echo("  [OK] 808: Slow Dance Breathe")

    gma.gui.msgbox("FX Sequences Done",
        "8 FX sequences created (801-808):\n\n" ..
        "801  Room Pulse\n" ..
        "802  Aerial Beam Storm\n" ..
        "803  Hue Chase FOH→Stage\n" ..
        "804  Pan Pendulum Cross\n" ..
        "805  Strobe Depth Chase\n" ..
        "806  Proscenium Frame Pulse\n" ..
        "807  Breathing Room\n" ..
        "808  Slow Dance Breathe\n\n" ..
        "Assign to executor faders on Page 1.")
end

return run
