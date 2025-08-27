#!/usr/bin/env python3
"""
Convert Trin vehicle JSON files to the new format with detailed feedback.

Features:
- Removes // comments before JSON parsing (reports lines affected).
- Interactive per-file conversion toggles (parts / definitions / general).
- Optional setting of default parts (asks once whether you want to change them).
- Explicit, readable feedback for each modification or skip.
- Auto-fix for general.health when converting "general":
    * If general.health is missing or equals 100, sets it to int(motorized.emptyMass/10).
    * Asks for emptyMass if missing; creates 'motorized' or 'general' objects if needed.
- Per-file summary of changes.

Note: This script keeps the original interactive prompts for choices and missing values.
"""

import os
import json
import argparse

# ---------- Simple logging helpers ----------
def info(msg):
    print(f"[INFO] {msg}")

def warn(msg):
    print(f"[WARN] {msg}")

def step(msg):
    print(f"\n=== {msg} ===")

def change(msg):
    print(f"[CHANGE] {msg}")

def skip(msg):
    print(f"[SKIP] {msg}")

# ---------- Original helpers with feedback tweaks ----------

def ask_default_wheel_CT():
    default_wheel = input('Enter the default wheel CT: ')
    converted = convert_CT_to_material_syntax(default_wheel)
    info(f"Default wheel CT converted to material syntax: {converted}")
    return converted

def ask_default_seat_CT():
    default_seat = input('Enter the default seat CT: ')
    converted = convert_CT_to_material_syntax(default_seat)
    info(f"Default seat CT converted to material syntax: {converted}")
    return converted

def ask_default_engine_CT():
    default_engine = input('Enter the default engine CT: ')
    converted = convert_CT_to_material_syntax(default_engine)
    info(f"Default engine CT converted to material syntax: {converted}")
    return converted

def ask_wheel_layout():
    front = input('Are the front wheels motorized? (y/n): ')
    rear = input('Are the rear wheels motorized? (y/n): ')
    wheel_list = []
    if front.lower() == 'y':
        wheel_list.append(1)
        wheel_list.append(2)
    if rear.lower() == 'y':
        wheel_list.append(3)
        wheel_list.append(4)
    info(f"Linked wheel indices selected: {wheel_list or 'none'}")
    return wheel_list

def convert_CT_to_material_syntax(string):
    # "<mts:iv_tpp.wheel_offroad_4d16_1_chromic>" -> "iv_tpp:wheel_offroad_4d16_1_chromic"
    return string[5:-1].replace('.', ':')

def remove_json_comments(file_path):
    """Remove // comments from a JSON file and report which lines were affected."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    comment_lines = 0
    for i, line in enumerate(lines, start=1):
        original = line
        if '//' in line:
            line = line.split('//', 1)[0]
            if line.rstrip("\n") != original.rstrip("\n"):
                comment_lines += 1
        cleaned_lines.append(line)

    if comment_lines > 0:
        info(f"Removed/trimmed // comments on {comment_lines} line(s).")
    else:
        info("No // comments found.")
    return ''.join(cleaned_lines)

def all_parts_have_default(data, part_type):
    return all('defaultPart' in part and part_type in part.get('types', []) for part in data.get('parts', []))

# ---------- CLI ----------
parser = argparse.ArgumentParser(description='Convert vehicle JSON files to the new format (verbose).')
parser.add_argument('folder', type=str, help='The folder containing JSON files to convert.')
args = parser.parse_args()

folder = args.folder
if not os.path.isdir(folder):
    raise SystemExit(f"Folder not found: {folder}")

files = sorted(os.listdir(folder))
info(f"Scanning folder: {folder}")
info(f"Found {len(files)} entries (will skip non-.json files).")

# ---------- Process each JSON ----------
for short_name in files:
    path = os.path.join(folder, short_name)

    if not short_name.endswith('.json'):
        skip(f"{short_name}: not a .json file.")
        continue

    step(f"Processing file: {short_name}")
    info("Reading and cleaning JSON (remove // comments)")
    try:
        cleaned_json_content = remove_json_comments(path)
    except Exception as e:
        warn(f"Failed to read/clean file: {e}")
        continue

    convert = input(f'Convert {short_name}? (y/n): ')
    if convert.lower() != 'y':
        skip("User chose not to convert this file.")
        continue

    convert_parts = input('Convert parts? (y/n): ')
    convert_definitions = input('Convert definitions? (y/n): ')
    convert_general = input('Convert general? (y/n): ')

    # Summary counters for this file
    summary = {
        "parts_processed": 0,
        "parts_default_added": 0,
        "parts_engine_linkedparts_set": 0,
        "parts_types_normalized_lightbar": 0,
        "parts_types_normalized_cratebarrel": 0,
        "definitions_updated": 0,
        "motorized_created": False,
        "general_created": False,
        "emptyMass_set": False,
        "health_set": False,
        "health_replaced_100": False,
        "health_left_as_is": False
    }

    try:
        data = json.loads(cleaned_json_content)
        info("JSON parsed successfully.")
    except json.JSONDecodeError as e:
        warn(f"JSON parsing failed: {e}")
        continue

    # Basic structure checks
    if 'parts' not in data or not isinstance(data['parts'], list):
        warn("'parts' key missing or not a list. Some operations may be skipped.")

    info(f"Parts count: {len(data.get('parts', []))}")

    # ---------- Convert Parts ----------
    if convert_parts.lower() == 'y':
        step("Converting parts")

        # NEW: ask if user wants to set/override defaults at all
        change_defaults = input('Do you want to set/override default parts for missing defaults (wheels/seats/engines)? (y/n): ').strip().lower()
        if change_defaults not in ('y', 'n'):
            warn("Unrecognized answer; defaulting to 'n' (do not change defaults).")
            change_defaults = 'n'

        default_wheel = None
        default_seat = None
        default_engine = None

        if change_defaults == 'y':
            if not all_parts_have_default(data, 'ground_wheel'):
                info("Not all wheel parts have a defaultPart. Will ask for default wheel CT.")
                default_wheel = ask_default_wheel_CT()
            else:
                info("All ground_wheel parts already have defaultPart. No default wheel prompt needed.")

            if not all_parts_have_default(data, 'seat'):
                info("Not all seat parts have a defaultPart. Will ask for default seat CT.")
                default_seat = ask_default_seat_CT()
            else:
                info("All seat parts already have defaultPart. No default seat prompt needed.")

            if not all_parts_have_default(data, 'engine_car'):
                info("Not all engine_car parts have a defaultPart. Will ask for default engine CT.")
                default_engine = ask_default_engine_CT()
            else:
                info("All engine_car parts already have defaultPart. No default engine prompt needed.")
        else:
            skip("User chose not to set/override default parts; will not prompt for CTs and will not add new defaultPart values.")

        for idx, part in enumerate(data.get('parts', []), start=1):
            summary["parts_processed"] += 1
            ppos = part.get('pos', f"index:{idx}")

            if 'types' not in part:
                warn(f"Part {ppos}: missing 'types'. Skipping this part.")
                continue

            types = part['types']
            info(f"Part {ppos}: types={types}")

            if 'defaultPart' not in part:
                # Wheels
                if ('ground_wheel' in types or 'wheel' in types) and change_defaults == 'y':
                    if default_wheel:
                        part['defaultPart'] = default_wheel
                        summary["parts_default_added"] += 1
                        change(f"Part {ppos}: set defaultPart (wheel) -> {default_wheel}")
                    else:
                        skip(f"Part {ppos}: default wheel not provided; left without defaultPart.")
                elif 'ground_wheel' in types or 'wheel' in types:
                    skip(f"Part {ppos}: wheel defaultPart not set (per user choice).")

                # Seat
                if 'seat' in types:
                    if change_defaults == 'y':
                        if default_seat:
                            part['defaultPart'] = default_seat
                            summary["parts_default_added"] += 1
                            change(f"Part {ppos}: set defaultPart (seat) -> {default_seat}")
                        else:
                            skip(f"Part {ppos}: default seat not provided; left without defaultPart.")
                    else:
                        skip(f"Part {ppos}: seat defaultPart not set (per user choice).")

                    # Additional seat fields (these are still safe to set even if defaultPart not changed)
                    if 'toneIndex' not in part:
                        part['toneIndex'] = 1
                        change(f"Part {ppos}: set toneIndex -> 1")
                    else:
                        skip(f"Part {ppos}: toneIndex already present ({part['toneIndex']}).")
                    if 'interactableVariables' not in part:
                        part['interactableVariables'] = [[]]
                        change(f"Part {ppos}: set interactableVariables -> [[]]")
                    else:
                        skip(f"Part {ppos}: interactableVariables already present.")

                # Engine
                if 'engine_car' in types:
                    if change_defaults == 'y':
                        if default_engine:
                            part['defaultPart'] = default_engine
                            summary["parts_default_added"] += 1
                            change(f"Part {ppos}: set defaultPart (engine_car) -> {default_engine}")
                        else:
                            skip(f"Part {ppos}: default engine not provided; left without defaultPart.")
                        # Ask wheel layout and set linkedParts only when we’re in engine default setting flow
                        wheels = ask_wheel_layout()
                        part['linkedParts'] = wheels
                        summary["parts_engine_linkedparts_set"] += 1
                        change(f"Part {ppos}: set linkedParts -> {wheels}")
                    else:
                        skip(f"Part {ppos}: engine defaultPart not set and linkedParts not asked (per user choice).")

            else:
                skip(f"Part {ppos}: defaultPart already present ({part['defaultPart']}).")

            # Normalize types for lightbar/roofdevice/gyrophare
            if ('generic_roofdevice' in types or 'generic_lightbar' in types or 'generic_gyrophare' in types):
                if types != ["generic_lightbar", "generic_roofdevice", "generic_gyrophare"]:
                    part['types'] = ["generic_lightbar", "generic_roofdevice", "generic_gyrophare"]
                    summary["parts_types_normalized_lightbar"] += 1
                    change(f"Part {ppos}: normalized types -> {part['types']}")
                else:
                    skip(f"Part {ppos}: types already normalized for lightbar set.")

            # Normalize types for interactable_crate/barrel
            if ('interactable_crate' in types or 'interactable_barrel' in types):
                if part['types'] != ["interactable_crate", "interactable_barrel"]:
                    part['types'] = ["interactable_crate", "interactable_barrel"]
                    summary["parts_types_normalized_cratebarrel"] += 1
                    change(f"Part {ppos}: normalized types -> {part['types']}")
                else:
                    skip(f"Part {ppos}: types already normalized for crate/barrel.")

    # ---------- Convert Definitions ----------
    if convert_definitions.lower() == 'y':
        step("Converting definitions")
        def_map = {
            "_blue": (" - Electric Blue Paint, Gray Interior",
                      [["mts:iv_tpp.paint_bucket_electricblue:0:1", "minecraft:wool:4:2", "minecraft:wool:0:3"]],
                      ["_gray"]),
            "_brown": (" - Milk Coffee Paint, Tan Interior",
                       [["mts:iv_tpp.paint_bucket_milkcoffee:0:1", "minecraft:wool:4:2", "minecraft:wool:0:3"]],
                       ["_beige"]),
            "_light_blue": (" - Sky Blue Paint, Gray Interior",
                            [["mts:iv_tpp.paint_bucket_skyblue:0:1", "minecraft:wool:7:2", "minecraft:wool:8:3"]],
                            ["_gray"]),
            "_light_gray": (" - Silver Paint, Black Interior",
                            [["mts:iv_tpp.paint_bucket_silver:0:1", "minecraft:wool:7:2", "minecraft:wool:15:3"]],
                            ["_black"]),
            "_red": (" - Red Paint, Tan Interior",
                     [["mts:iv_tpp.paint_bucket_carminred:0:1", "minecraft:wool:4:2", "minecraft:wool:0:3"]],
                     ["_beige"]),
            "_olive": (" - Soft Green Paint, Tan Interior",
                       [["mts:iv_tpp.paint_bucket_softgreen:0:1", "minecraft:wool:4:2", "minecraft:wool:0:3"]],
                       ["_beige"]),
            "_pure_black": (" - Pure Black Paint, Red Interior",
                            [["mts:iv_tpp.paint_bucket_pureblack:0:1", "minecraft:wool:7:2", "minecraft:wool:14:3"]],
                            ["_red"]),
            "_pure_white": (" - Pure White Paint, Red Interior",
                            [["mts:iv_tpp.paint_bucket_purewhite:0:1", "minecraft:wool:7:2", "minecraft:wool:14:3"]],
                            ["_red"]),
            "_diamond": (" - Diamond Wrap, White Interior",
                         [["mts:iv_tpp.wrap_roll_diamond:0:1", "minecraft:wool:7:2", "minecraft:wool:11:3"]],
                         ["_white"]),
        }

        defs = data.get("definitions", [])
        if not defs:
            warn("No 'definitions' array found; skipping definitions conversion.")
        for i, definition in enumerate(defs, start=1):
            sub = definition.get("subName")
            nm = definition.get("name")
            if nm is None:
                warn(f"Definition #{i} (subName={sub}): missing 'name'. Skipping.")
                continue

            if sub in def_map:
                suffix, extra_mats, tones = def_map[sub]
                before = nm
                # Apply
                definition["name"] = nm + suffix
                definition["extraMaterialLists"] = extra_mats
                definition["partTones"] = tones
                summary["definitions_updated"] += 1
                change(f"Definition #{i} subName='{sub}':")
                info(f" - name: '{before}' -> '{definition['name']}'")
                info(f" - extraMaterialLists set to: {extra_mats}")
                info(f" - partTones set to: {tones}")
            else:
                skip(f"Definition #{i} subName='{sub}': no mapping; left unchanged.")

    # ---------- Convert General ----------
    if convert_general.lower() == 'y':
        step("Converting general (emptyMass & health)")

        # Ensure 'motorized' exists
        if 'motorized' not in data or not isinstance(data['motorized'], dict):
            data['motorized'] = {}
            summary["motorized_created"] = True
            change("Created 'motorized' object (was missing).")
        else:
            skip("'motorized' object already present.")

        # Ensure emptyMass exists
        if 'emptyMass' not in data['motorized']:
            val = input('The entry "motorized.emptyMass" is missing. Please provide a numeric value: ')
            try:
                data['motorized']['emptyMass'] = int(val)
                summary["emptyMass_set"] = True
                change(f"Set motorized.emptyMass -> {data['motorized']['emptyMass']}")
            except ValueError:
                warn('Invalid value for "emptyMass". Skipping health computation for this file.')
        else:
            info(f"motorized.emptyMass present: {data['motorized']['emptyMass']}")

        # Compute/Apply health only if emptyMass is valid
        empty_mass = data.get('motorized', {}).get('emptyMass')
        if isinstance(empty_mass, (int, float)):
            new_health = int(empty_mass / 10)
            info(f"Computed health from emptyMass/10 -> {new_health}")

            # Ensure 'general' exists
            if 'general' not in data or not isinstance(data['general'], dict):
                data['general'] = {}
                summary["general_created"] = True
                change("Created 'general' object (was missing).")
            else:
                skip("'general' object already present.")

            current_health = data['general'].get('health', None)
            if current_health is None:
                data['general']['health'] = new_health
                summary["health_set"] = True
                change(f"general.health was missing -> set to {new_health}")
            elif current_health == 100:
                data['general']['health'] = new_health
                summary["health_replaced_100"] = True
                change(f"general.health was 100 -> replaced with {new_health}")
            else:
                summary["health_left_as_is"] = True
                skip(f"general.health is {current_health} -> left unchanged.")
        else:
            skip("emptyMass missing or invalid; health not computed.")

    # ---------- Save ----------
    step("Saving changes")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        info("File written successfully.")
    except Exception as e:
        warn(f"Failed to write file: {e}")
        continue

    # ---------- Per-file summary ----------
    step("Summary")
    print(
        f"- Parts processed: {summary['parts_processed']}\n"
        f"- defaultPart added: {summary['parts_default_added']}\n"
        f"- linkedParts set on engines: {summary['parts_engine_linkedparts_set']}\n"
        f"- Types normalized (lightbar set): {summary['parts_types_normalized_lightbar']}\n"
        f"- Types normalized (crate/barrel): {summary['parts_types_normalized_cratebarrel']}\n"
        f"- Definitions updated: {summary['definitions_updated']}\n"
        f"- Created 'motorized': {summary['motorized_created']}\n"
        f"- Created 'general': {summary['general_created']}\n"
        f"- emptyMass set: {summary['emptyMass_set']}\n"
        f"- health set (missing): {summary['health_set']}\n"
        f"- health replaced (100): {summary['health_replaced_100']}\n"
        f"- health left as is: {summary['health_left_as_is']}"
    )

    info(f"{short_name} has been converted.")
