'''
This script is used to convert the vehicle JSON files to the new format.

It will read all jsons within a given folder, and go through them all to update them all.
'''

import os
import json
import argparse

# function to ask default wheel CT
def ask_default_wheel_CT():
    # Ask the user for the default wheel CT
    default_wheel = input('Enter the default wheel CT: ')

    # Return the default wheel CT
    return convert_CT_to_material_syntax(default_wheel)

# function to ask default seat CT
def ask_default_seat_CT():
    # Ask the user for the default seat CT
    default_seat = input('Enter the default seat CT: ')

    # Return the default seat CT
    return convert_CT_to_material_syntax(default_seat)

# function to ask default engine CT
def ask_default_engine_CT():
    # Ask the user for the default engine CT
    default_engine = input('Enter the default engine CT: ')

    # Return the default engine CT
    return convert_CT_to_material_syntax(default_engine)

# function to ask for wheel layout
def ask_wheel_layout():
    # Ask the user for the wheel layout
    front = input('Are the front wheels motorized? (y/n): ')
    rear = input('Are the rear wheels motorized? (y/n): ')

    # Return the wheel layout
    wheel_list = []
    if front.lower() == 'y':
        # add 1 and 2 to the list
        wheel_list.append(1)
        wheel_list.append(2)
    if rear.lower() == 'y':
        # add 3 and 4 to the list
        wheel_list.append(3)
        wheel_list.append(4)
    
    print(wheel_list)
    return wheel_list

# function to convert CT syntax to material syntax
def convert_CT_to_material_syntax(string):
    # convert something like "<mts:iv_tpp.wheel_offroad_4d16_1_chromic>"
    # to "iv_tpp:wheel_offroad_4d16_1_chromic"
    # remove "<mts:" and ">", replace "." with ":"
    return string[5:-1].replace('.', ':')



# Use argparse to get the folder to convert.
parser = argparse.ArgumentParser(description='Convert vehicle JSON files to the new format.')
parser.add_argument('folder', type=str, help='The folder to convert the JSON files in.')
args = parser.parse_args()

# Get the folder
folder = args.folder

# Get all the files in the folder
files = os.listdir(folder)

# Go through all the files
for file in files:
    # Skip non-json files
    if not file.endswith('.json'):
        continue

    # Ask the user if he wants to convert this file
    convert = input(f'Convert {file}? (y/n): ')

    # If the user doesn't want to convert this file, skip it
    if convert.lower() != 'y':
        continue

    # Ask the user if he wants to convert parts
    convert_parts = input(f'Convert parts? (y/n): ')

    # Ask the user if he wants to convert definitions
    convert_definitions = input(f'Convert definitions? (y/n): ')

    # Ask the user if he wants to convert general
    convert_general = input(f'Convert general? (y/n): ')

    # If the user doesn't want to convert parts, skip it
    if convert_parts.lower() == 'y':
        default_wheel = ask_default_wheel_CT()
        default_seat = ask_default_seat_CT()
        default_engine = ask_default_engine_CT()

    # Open the file
    with open(file, 'r') as f:
        # Load the JSON
        data = json.load(f)

        # In the "parts" key: tell how long the list is
        print(len(data['parts']))

        # If the user wants to convert parts
        if convert_parts.lower() == 'y':
            # for all parts, check the "types" key
            for part in data['parts']:
                # if "defaultPart" is not in the list
                if 'defaultPart' not in part:
                    print(part['types'])
                    # If "ground_wheel" is in the list
                    if 'ground_wheel' in part['types']:
                        # Add "defaultPart": *default_wheel* after the "types" key
                        part['defaultPart'] = default_wheel
                    # If "seat" is in the list
                    if 'seat' in part['types']:
                        # Add "defaultPart": *default_seat* after the "types" key
                        part['defaultPart'] = default_seat
                        # Add "toneIndex": 1
                        part['toneIndex'] = 1
                        # Add "interactableVariables": [[]]
                        part['interactableVariables'] = [[]]
                    # If "engine_car" is in the list
                    if 'engine_car' in part['types']:
                        # Add "defaultPart": *default_engine* after the "types" key
                        part['defaultPart'] = default_engine
                        # Add "linkedParts": []
                        wheels = ask_wheel_layout()
                        part['linkedParts'] = wheels
                    # If "generic_roofdevice", "generic_lightbar" or "generic_gyrophare" is in the list
                    if 'generic_roofdevice' in part['types'] or 'generic_lightbar' in part['types'] or 'generic_gyrophare' in part['types']:
                        # Replace the list with [ "generic_lightbar", "generic_roofdevice", "generic_gyrophare"]
                        part['types'] = ["generic_lightbar", "generic_roofdevice", "generic_gyrophare"]
                    # If "interactable_crate" or "interactable_barrel" is in the list
                    if 'interactable_crate' in part['types'] or 'interactable_barrel' in part['types']:
                        # Replace the list with ["interactable_crate", "interactable_barrel"]
                        part['types'] = ["interactable_crate", "interactable_barrel"]

        # If the user wants to convert definitions
        if convert_definitions.lower() == 'y':
            # for all definitions, modify the "name" key
            for definition in data["definitions"]:
                # switch on the "subName"
                if definition["subName"] == "_blue":
                    definition["name"] =  definition["name"] + " - Electric Blue Paint, Tan Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_electricblue:0:1",
                        "minecraft:wool:4:2",
                        "minecraft:wool:0:3"
                    ]]
                    definition["partTones"] = [
                        "_beige"
                    ]
                elif definition["subName"] == "_brown":
                    definition["name"] =  definition["name"] + " - Milk Coffee Paint, Tan Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_milkcoffee:0:1",
                        "minecraft:wool:4:2",
                        "minecraft:wool:0:3"
                    ]]
                    definition["partTones"] = [
                        "_beige"
                    ]
                elif definition["subName"] == "_light_blue":
                    definition["name"] =  definition["name"] + " - Sky Blue Paint, Gray Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_skyblue:0:1",
                        "minecraft:wool:7:2",
                        "minecraft:wool:8:3"
                    ]]
                    definition["partTones"] = [
                        "_gray"
                    ]
                elif definition["subName"] == "_light_gray":
                    definition["name"] =  definition["name"] + " - Silver Paint, Black Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_silver:0:1",
                        "minecraft:wool:7:2",
                        "minecraft:wool:15:3"
                    ]]
                    definition["partTones"] = [
                        "_black"
                    ]
                elif definition["subName"] == "_olive":
                    definition["name"] =  definition["name"] + " - Soft Green Paint, Tan Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_softgreen:0:1",
                        "minecraft:wool:4:2",
                        "minecraft:wool:0:3"
                    ]]
                    definition["partTones"] = [
                        "_beige"
                    ]
                elif definition["subName"] == "_pure_black":
                    definition["name"] =  definition["name"] + " - Pure Black Paint, Red Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_pureblack:0:1",
                        "minecraft:wool:7:2",
                        "minecraft:wool:14:3"
                    ]]
                    definition["partTones"] = [
                        "_red"
                    ]
                elif definition["subName"] == "_pure_white":
                    definition["name"] =  definition["name"] + " - Pure White Paint, Red Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.paint_bucket_purewhite:0:1",
                        "minecraft:wool:7:2",
                        "minecraft:wool:14:3"
                    ]]
                    definition["partTones"] = [
                        "_red"
                    ]
                elif definition["subName"] == "_diamond":
                    definition["name"] =  definition["name"] + " - Diamond Wrap, Gray & Blue Interior"
                    definition["extraMaterialLists"] = [[
                        "mts:iv_tpp.wrap_roll_diamond:0:1",
                        "minecraft:wool:7:2",
                        "minecraft:wool:11:3"
                    ]]
                    definition["partTones"] = [
                        "_gray_blue"
                    ]

        # If the user wants to convert general
        if convert_general.lower() == 'y':
            # Modify the health
            health = int(data['motorized']['emptyMass'] / 10)

        # Save the JSON
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    # Print that the file has been converted
    print(f'{file} has been converted.')




