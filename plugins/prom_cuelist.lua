-- ================================================================
-- prom_cuelist.lua
-- FCHS Prom 2026 — Build master show cue list (Sequence 900)
-- ================================================================
-- INSTALL: Copy to [MA3 root]/shared/resource/lib/plugins/
-- RUN:     Plugin "prom_cuelist"
-- WHEN:    Run LAST — after presets, groups, and FX sequences
-- RESULT:  Sequence 900 with 17 named cues, assigned to Page 2 Exec 1
-- ================================================================

local SEQ = 900

local function cue(number, label, fade_in, fade_out, trigger, follow_delay)
    fade_in      = fade_in      or 2
    fade_out     = fade_out     or 2
    trigger      = trigger      or "Go"
    follow_delay = follow_delay or 0
    gma.cmd(string.format('Store Cue %d.%s "%s" /nc', SEQ, number, label))
    gma.sleep(100)
    gma.cmd(string.format('Cue %d.%s Property "InFade" %s',  SEQ, number, fade_in))
    gma.sleep(30)
    gma.cmd(string.format('Cue %d.%s Property "OutFade" %s', SEQ, number, fade_out))
    gma.sleep(30)
    gma.cmd(string.format('Cue %d.%s Property "Trigger" "%s"', SEQ, number, trigger))
    gma.sleep(30)
    if follow_delay > 0 then
        gma.cmd(string.format('Cue %d.%s Property "FollowDelay" %s', SEQ, number, follow_delay))
        gma.sleep(30)
    end
    gma.echo(string.format("  Cue %s: %s", number, label))
end

local function run()

    if not gma.gui.confirm("FCHS Prom — Cue List",
        "Build Sequence 900 'FCHS Prom 2026' with 17 named cues?\n\n" ..
        "Existing Sequence 900 will be deleted.\n\n" ..
        "This creates structure only — program content into cues manually.") then
        return
    end

    gma.cmd(string.format('Delete Sequence %d /nc', SEQ))
    gma.sleep(100)
    gma.cmd(string.format('Store Sequence %d "FCHS Prom 2026" /nc', SEQ))
    gma.sleep(150)
    gma.echo("=== Building FCHS Prom 2026 cue list ===")

    gma.cmd("Group 112") gma.sleep(30)
    gma.cmd("Group 111") gma.sleep(30)
    gma.cmd("Group 113") gma.sleep(30)
    gma.cmd("Group 109") gma.sleep(30)
    gma.cmd('Attribute "Dimmer" At 0') gma.sleep(30)
    cue("0.5", "** BLACKOUT **", 0, 0, "Go")
    gma.cmd("Clear") gma.sleep(50)

    cue("1",   "Arrival - Pre Show",        5,   3,   "Go")
    cue("2",   "Grand Entrance",            3,   2,   "Go")
    cue("3",   "Applause Flash",            0,   1.5, "Follow", 0)
    cue("4",   "Opening Dance Floor",       4,   3,   "Go")
    cue("5",   "Peak Dance Floor",          2,   2,   "Go")
    cue("6",   "BIG DROP",                  0,   0,   "Go")
    cue("7",   "Prom Court Walk",           3,   2,   "Go")
    cue("7.5", "Name Flash",                0,   0.8, "Follow", 0)
    cue("8",   "Crown Build - Step1",       2,   1,   "Go")
    cue("8.5", "Crown Build - Step2",       1,   0.5, "Follow", 2)
    cue("8.8", "Crown Build - Hold Breath", 0.5, 0,   "Follow", 3)
    cue("9",   "=== CROWN REVEAL ===",      0,   0,   "Go")
    cue("10",  "Post-Crown Hold",           3,   2,   "Go")
    cue("11",  "Slow Dance / Ballad",       5,   4,   "Go")
    cue("12",  "Dance Floor Return",        4,   3,   "Go")
    cue("13",  "Finale Build",              4,   3,   "Go")
    cue("14",  "Last Song",                 3,   2,   "Go")
    cue("15",  "Finale Cascade",            0.3, 0,   "Go")

    gma.cmd('Attribute "Dimmer" At 0') gma.sleep(30)
    cue("99", "END - Blackout", 10, 0, "Go")
    gma.cmd("Clear") gma.sleep(50)

    gma.cmd(string.format('Assign Sequence %d "Page2.1" /nc', SEQ))
    gma.sleep(100)

    gma.gui.msgbox("Cue List Done",
        "Sequence 900 'FCHS Prom 2026' — 17 cues.\n" ..
        "Assigned to Page 2, Exec 1.\n\n" ..
        "Next: open each cue and add content using\n" ..
        "Preset Pool 4 colors and Groups 101-113.\n\n" ..
        "Crown Reveal (Cue 9) is the most important —\nprogram it first.")
end

return run
