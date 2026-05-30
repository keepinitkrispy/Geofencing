-- ================================================================
-- prom_color_presets.lua
-- FCHS Prom 2026 — Build color presets in Preset Pool 4
-- ================================================================
-- INSTALL: Copy to [MA3 root]/shared/resource/lib/plugins/
-- RUN:     Plugin "prom_color_presets"   (or assign to a button)
-- WHEN:    Run once, after patching, with fixtures addressed
-- ================================================================

local function run()

    if not gma.gui.confirm("FCHS Prom — Colors",
        "Create 7 prom color presets in Preset Pool 4 (slots 101-107)?\n\nExisting presets in those slots will be overwritten.") then
        return
    end

    -- Hue in degrees (0-360), Saturation 0-100
    -- MA3 converts Hue/Sat to each fixture's native color space (RGB/CMY/etc.)
    local palette = {
        { slot = 101, name = "Prom-PatriotBlue",  hue = 210, sat = 80  },
        { slot = 102, name = "Prom-PatriotGold",  hue = 43,  sat = 100 },
        { slot = 103, name = "Prom-SoftGold",     hue = 43,  sat = 55  },
        { slot = 104, name = "Prom-DeepBlue",     hue = 225, sat = 92  },
        { slot = 105, name = "Prom-Champagne",    hue = 38,  sat = 22  },
        { slot = 106, name = "Prom-Lavender",     hue = 270, sat = 52  },
        { slot = 107, name = "Prom-White",        hue = 0,   sat = 0   },
    }

    gma.echo("--- FCHS Prom: building color presets ---")

    for _, c in ipairs(palette) do
        -- Select all fixtures in show
        gma.cmd("SelectAll")
        gma.sleep(50)

        -- Set Hue and Saturation via MA3 unified color model
        gma.cmd(string.format('Attribute "Hue" At %d', c.hue))
        gma.sleep(30)
        gma.cmd(string.format('Attribute "Saturation" At %d', c.sat))
        gma.sleep(30)

        -- Store into Color preset pool (pool 4), named slot
        gma.cmd(string.format('Store Preset 4.%d "%s" /nc /remove', c.slot, c.name))
        gma.sleep(150)

        -- Clear programmer before next color
        gma.cmd("Clear")
        gma.sleep(50)

        gma.echo(string.format("  [OK] %s → Preset 4.%d", c.name, c.slot))
    end

    gma.gui.msgbox("Presets Done",
        "7 presets stored in Pool 4:\n\n" ..
        "101  Prom-PatriotBlue\n" ..
        "102  Prom-PatriotGold\n" ..
        "103  Prom-SoftGold\n" ..
        "104  Prom-DeepBlue\n" ..
        "105  Prom-Champagne\n" ..
        "106  Prom-Lavender\n" ..
        "107  Prom-White")
end

return run
