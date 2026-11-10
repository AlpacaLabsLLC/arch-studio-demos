# Sheds in Rhino 9 with Claude: one model, a bill of materials, one framing sheet

> **Concept only.** The model and the drawing this demo produces are concept studies. They are not engineered, not checked against any local code, and not for construction. Nobody has had the scripts print a sheet on paper. Do not build from them.

This folder holds the scripts and the Grasshopper definition behind the newsletter piece "This drawing was made by AI". In that session Claude, working inside Rhino 9, built a small group of sheds, each housing a toilet, from one generator script, then produced a bill of materials and an ARCH D framing sheet from the same model.

The idea the demo tests: give Claude Rhino's own tools (hidden-line projection, layouts, detail views, display modes, PDF export, Grasshopper) and let it drive them with scripts. Almost every step in the original session was a Python script calling Rhino directly. The scripts here are those scripts.

## What you need

- **Rhino 9** (the session ran in Rhino 9; nothing here was tried in other versions).
- **Claude with the Rhino tools**, meaning a Claude client that can run Python inside the open Rhino document, capture viewports, save the file and work with Grasshopper. The original session used the Rhino 9 AI panel, which runs Claude Code with those tools.
- Grasshopper (ships with Rhino 9). The generator runs in a Python 3 component.
- An empty folder to hold this one, for example `~/sheds-demo`.

## What is in the folder

| Path | What it is |
|---|---|
| `grasshopper/sheds-r6.gh` | Grasshopper definition: one number slider named `Cube size` feeding one Python 3 component named `Sheds`, which contains the generator source. |
| `scripts/sheds_gen_r6.py` | The generator. One driver, the cube size `C` (metres). Returns one closed solid per element (piers, framing, deck, ramp, steps, walls, doors, curved rib roofs with thatch, fixtures, plumbing to a septic pit). Each solid carries its layer and object name as user strings. Builds four layouts, A to D. |
| `scripts/sheds_bake_r6.py` | Reads the solids from the Grasshopper component, sets the slider, and bakes them into the Rhino document on layers `Sheds Run 6::Option A` to `D`. |
| `scripts/bom_row6.py` | Bill of materials, one CSV per layout. Every object must map to a line or the script stops with `unmapped ...`. The Source column says whether a quantity was measured from the model or calculated, and marks materials and stock lengths that are assumed. |
| `scripts/sheet_a101_setup.py` | Sheet setup: creates the ARCH D layout page `A-101 Exploded Framing`, its main detail at 1:40, the border, the explosion guides and the `_a101` document string the other sheet scripts read. Run once, after the bake and BOM. New in this folder; rebuilt from the original session. |
| `scripts/sheet_a101_stage.py` | Sheet step 1: copies layout A into three exploded groups (floor, walls, roof) on `Sheet A-101` layers. |
| `scripts/sheet_a101_bw.py` | Sheet step 2: runs Rhino's hidden-line projection on the exploded copies and draws black-and-white linework with separate weights for outlines and edges. |
| `scripts/sheet_a101_annotate.py` | Sheet step 3: framing key, notes, title block and the bill of materials table (read from the layout A CSV). |
| `scripts/sheet_a101_bubbles.py` | Sheet step 4: the two circular details, D1 (rib at wall plate) and D2 (deck girder at concrete pier), each cut from the real joint and tied to it by a leader. |

## Steps

Copy the contents of this folder to `~/sheds-demo/`, so that `~/sheds-demo/scripts/` exists. The scripts and the reproduce prompt below both use that path, and the Rhino AI panel has no working folder of its own to resolve a relative path against. If you keep the folder somewhere else, change the three path lines (`GEN` in `sheds_bake_r6.py`, `root` in `bom_row6.py`, the CSV path in `sheet_a101_annotate.py`) and the path in the prompt.

Steps 1 and 2 are yours to do by hand. Steps 3 to 6 are what the reproduce prompt below asks Claude to do, so you can paste that prompt instead of asking for them one at a time.

1. **Start clean.** Open Rhino 9 and make a new file, with no other document open (see the warning below). Use a new file: `bake` deletes any existing `Sheds Run 6` layer before it bakes. The generator works in metres, so run `Units` and set the model units to meters.
2. **Open the Grasshopper definition.** In Rhino run `Grasshopper`, then File > Open Document and choose `~/sheds-demo/grasshopper/sheds-r6.gh`. `~` is your home folder; on macOS, press Cmd+Shift+G in the Open dialog and type the path. Check that the canvas has the `Cube size` slider and the `Sheds` component.
3. **Bake the model.** Ask Claude something like: *"Load ~/sheds-demo/scripts/sheds_bake_r6.py in this document and call bake(doc, 2.40). Then show me a viewport image of each layout."* The call sets the slider to 2.40 m, solves, and bakes four layouts. Change the number to resize everything; the other dimensions follow. `reload_source()` in that script re-reads the generator from `GEN`, which you need only if you edit the generator file.
4. **Write the bills of materials.** Ask Claude to run `scripts/bom_row6.py`. It writes `bom-run6-option-A.csv` to `D` into `~/sheds-demo/bom-row6/`. Read the Source column: it says whether each quantity was measured from the model or calculated, and flags assumed materials and stock lengths. Nails and screws are not counted, and the pier line notes that no footing or reinforcement is included. Anything missing from the CSV is not counted, which is different from zero.
5. **Set up the sheet.** Ask Claude to load `scripts/sheet_a101_setup.py` and call `main(doc)`. It needs model units in metres and sets the page units to inches.
6. **Make the sheet.** Ask Claude to run the sheet scripts in this order: `sheet_a101_stage.py` (call `stage(doc, group)` once each for `Floor`, `Walls`, `Roof`), `sheet_a101_bw.py` (`main(doc)`), `sheet_a101_annotate.py` (`run(doc)`), then `sheet_a101_bubbles.py` (`run(doc, bw)`, where `bw` is the loaded `sheet_a101_bw` namespace). The linework is static, so after any change to the model run the sheet scripts again.

## Starter prompts

Both prompts were written for this README. Neither is the prompt from the original session. The first was run once, in the Rhino AI panel on Claude Opus: it ran all seven steps with the scripts unchanged and no errors. The second has not been tried.

**Reproduce the same sheds and sheet.** First copy this folder to `~/sheds-demo/` and do steps 1 and 2 above, so that you have a new file in metres with `sheds-r6.gh` open. Then paste this into a new chat in the Rhino AI panel. The prompt tells Claude not to rewrite the scripts because agents often rebuild a script instead of running it, and then you are no longer testing these files. The scripts have produced a sheet from this folder; the prompt ran once in the panel, as noted above.

```text
Reproduce this demo by running the scripts in ~/sheds-demo/scripts, in order, exactly as they are. Do not rewrite, rebuild, simplify or replace any script, and do not write your own version of any step. If a script fails, stop and show me the error before changing anything. The model units are metres and ~/sheds-demo/grasshopper/sheds-r6.gh is open in Grasshopper.

Use run_python, with one call for each numbered step. Start every call with these lines, unchanged:

    import os
    doc = __rhino_doc__
    def load(name):
        path = os.path.expanduser("~/sheds-demo/scripts/" + name)
        ns = {"__rhino_doc__": doc}
        exec(compile(open(path, encoding="utf-8").read(), path, "exec"), ns)
        return ns

Then add the lines for that step:

1. Bake the model:
    print(load("sheds_bake_r6.py")["bake"](doc, 2.40))

2. Write the bills of materials. Loading this script runs it, and it prints any error instead of raising it, so read its output:
    load("bom_row6.py")

3. Set up the sheet:
    print(load("sheet_a101_setup.py")["main"](doc))

4. Stage the three groups:
    stage = load("sheet_a101_stage.py")["stage"]
    for group in ("Floor", "Walls", "Roof"):
        print(group, stage(doc, group))

5. Draw the linework:
    print(load("sheet_a101_bw.py")["main"](doc))

6. Annotate the sheet:
    print(load("sheet_a101_annotate.py")["run"](doc))

7. Add the two details. This one needs the sheet_a101_bw namespace as well:
    bw = load("sheet_a101_bw.py")
    print(load("sheet_a101_bubbles.py")["run"](doc, bw))

After each step, tell me what the script returned or printed.
```

**Use the skills on your own building.** Available once Arch Studio 1.5.3 is out.

> Use as-rhino-model to plan, build and check a model of my building in this Rhino document: [describe your building]. Then use as-rhino-fineline to make a black and white vector sheet of it, with a checked PDF. Report anything that fails.

## What was run, and what is unverified

The proof run was a script calling Rhino's tools directly, with no Claude in the loop. It shows that this folder reproduces the model and the sheet. On its own it does not show that an agent following a prompt will do the same; the panel run of the first starter prompt, once, is the evidence for that.

It ran once from an empty file, in the order above, in Rhino 9.0.26300.9402 on macOS. These changes were made around that run:

- **Hatch pattern, included in the run.** `sheet_a101_annotate.py` now creates the `Solid` hatch pattern when the file has none. A first pass stopped there, and the run below started again from an empty file with this fix in place.
- **Path lines, for the run only.** The run's copy of the folder pointed the three path lines described above at that copy. The scripts here use `~/sheds-demo/`.

Results of the run:

- `sheds_bake_r6.py` baked 7,251 objects at 2.40 m.
- `bom_row6.py` wrote all four CSVs with no `unmapped` error.
- `sheet_a101_setup.py` built the page and detail. Its view target matched the original session's saved value.
- `sheet_a101_stage.py` staged 857 floor, 364 wall and 305 roof objects.
- `sheet_a101_bw.py` drew the hidden-line linework from 1,526 solids, `sheet_a101_annotate.py` added the framing key, notes, title block and bill of materials table, and `sheet_a101_bubbles.py` added details D1 and D2.
- The finished sheet was exported to PDF and an image and looked at. It has the title block, notes, framing key, 16 callouts and both details. The D2 circle sits over the floor and ramp linework behind it, and the joint it marks lies inside the circle.
- `grasshopper/sheds-r6.gh`, reopened from the saved file, solved with no errors or warnings and returned 7,251 solids.

No part of this was checked by an engineer, printed on paper, or run on Windows.

**Known items in the model.** Measured in the run above, in all four layouts. They are left as the original session built them.

- **Ramp joists overlap the framing they land on.** Each of the 16 sloped ramp joists in a layout runs about 17 x 38 x 180 mm into a ramp girder ply, or into the deck framing at the top of the ramp, because the joist ends are cut square to the slope. In layout C one joist also clips a sill plate by about 1 x 9 x 38 mm.
- **The cold-water main stops short of the meter box.** The main runs under the box, 167.5 mm below the bottom of it, and nothing connects the two.

Other things to know:

- **Keep only one document open.** In an earlier run, another open Rhino document was marked as changed when the page was created: Rhino 9 on macOS wrote the page's id into that other document. Have only the new file open when you run the sheet setup.
- **Layout-specific numbers.** `sheet_a101_bubbles.py` contains positions measured for the 2.40 m cube, for example a pier picked by its position. Another cube size will need them adjusted, and the sheet positions assume the ARCH D page the setup creates.
- **Fonts.** The sheet text asks for Helvetica, which macOS has. Other systems may substitute a font.
- **The checker is not included.** The original model carried a requirements list and an automated check. That check is not part of this demo.
- **Standards used as stand-ins.** Accessibility and framing values follow US sources used as stand-ins (AWC WCD1 figure labels and general US practice). The structural chapters of the wood-frame standard were not read. Nothing was checked against any local code, site rule or permit.
- **Not compared.** The session did not repeat the work without Claude's Rhino tools, so this shows what happened and is not a measured comparison.

## Left out on purpose

The full Rhino models (very large), the session transcript, exported sheets and images, the CSV outputs, the earlier runs' scripts (rows 1 to 5), earlier sheet iterations, and the project's real name and location.
