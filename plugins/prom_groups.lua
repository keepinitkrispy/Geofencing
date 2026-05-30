-- ================================================================
-- prom_groups.lua
-- FCHS Prom 2026 — Interactive group builder for the prom show
-- ================================================================
-- INSTALL: Copy to [MA3 root]/shared/resource/lib/plugins/
-- RUN:     Plugin "prom_groups"
-- WHEN:    Run once, AFTER patching is complete
--          You will be prompted to select fixtures for each group
-- ================================================================

local function run()

    if not gma.gui.confirm("FCHS Prom — Build Groups",
        "Build 13 named groups for the prom show.\n\n" ..
        "You will be prompted to select fixtures for each group on the layout.\n" ..
        "Select fixtures, then press OK on each dialog.\nReady?") then
        return
    end

    local manual_groups = {
        { slot = 101, name = "Prom-FOH Spots",    hint = "Select FOH truss SPOT/BEAM fixtures on layout, then click OK." },
        { slot = 102, name = "Prom-Mid Spots",    hint = "Select MID-ROOM truss SPOT/BEAM fixtures, then click OK." },
        { slot = 103, name = "Prom-Stage Spots",  hint = "Select BACK/UPSTAGE SPOT/BEAM fixtures, then click OK." },
        { slot = 104, name = "Prom-FOH Wash",     hint = "Select FOH truss WASH fixtures, then click OK." },
        { slot = 105, name = "Prom-Mid Wash",     hint = "Select MID-ROOM WASH fixtures, then click OK." },
        { slot = 106, name = "Prom-Stage Wash",   hint = "Select BACK/UPSTAGE WASH fixtures, then click OK." },
        { slot = 107, name = "Prom-Pros Left",    hint = "Select PROSCENIUM LEFT LED strip(s), then click OK." },
        { slot = 108, name = "Prom-Pros Right",   hint = "Select PROSCENIUM RIGHT LED strip(s), then click OK." },
        { slot = 109, name = "Prom-All Blinders", hint = "Select ALL BLINDER fixtures, then click OK." },
        { slot = 110, name = "Prom-All Strobes",  hint = "Select ALL STROBE fixtures, then click OK." },
    }

    for _, g in ipairs(manual_groups) do
        gma.cmd("Clear")
        gma.sleep(100)
        gma.gui.msgbox("GROUP: " .. g.name, g.hint)
        gma.sleep(100)
        gma.cmd(string.format('Store Group %d "%s" /nc', g.slot, g.name))
        gma.sleep(150)
        gma.echo(string.format("  [OK] Group %d: %s", g.slot, g.name))
    end

    gma.echo("Building combined groups...")
    gma.sleep(200)

    gma.cmd("Group 101 + Group 102 + Group 103")
    gma.sleep(50)
    gma.cmd('Store Group 111 "Prom-All Spots" /nc')
    gma.sleep(150)
    gma.cmd("Clear")
    gma.echo("  [OK] Group 111: Prom-All Spots")

    gma.cmd("Group 104 + Group 105 + Group 106")
    gma.sleep(50)
    gma.cmd('Store Group 112 "Prom-All Wash" /nc')
    gma.sleep(150)
    gma.cmd("Clear")
    gma.echo("  [OK] Group 112: Prom-All Wash")

    gma.cmd("Group 107 + Group 108")
    gma.sleep(50)
    gma.cmd('Store Group 113 "Prom-Proscenium" /nc')
    gma.sleep(150)
    gma.cmd("Clear")
    gma.echo("  [OK] Group 113: Prom-Proscenium")

    gma.gui.msgbox("Groups Done",
        "13 groups created (101-113):\n\n" ..
        "101 FOH Spots  102 Mid Spots  103 Stage Spots\n" ..
        "104 FOH Wash   105 Mid Wash   106 Stage Wash\n" ..
        "107 Pros Left  108 Pros Right\n" ..
        "109 All Blinders  110 All Strobes\n" ..
        "111 All Spots  112 All Wash  113 Proscenium")
end

return run
