# Bug reporting & Feature suggestions
- Report issues through github interface (top bar)
- Feel free to suggest any feature/improvement in the form of a pull-request or via email (voblivion <at> hotmail <dot> fr)

# How to install

- Ensure blender version is 3.5 or above
- Ensure Trackmania2020 and NadeoImporter are installed (https://doc.trackmania.com/nadeo-importer/)
- Download ZIP from repository (github > green "Code" button > Download ZIP)
- Rename downloaded file into "Trackmania.zip"
- Install into blender (Edit > Preferences > Add-ons > Install > Select "Trackmania.zip")
- Change Author Name to yours (Edit > Preferences > Add-ons > Trackmania > Author Name)

Since this addon is still heavily WIP, you can also clone this repository into Blender's addons folders too keep it up-to-date more easily (make sure you then Install it into blender through \_\_init\_\_.py file).

# How to use

## Collections

By default, collections are used to organize folders/sub-folders in which items will be exported.

- Export type tells whether collection should be exported into its own item ("Collection") or not ("None").
- Path type tells how to name exported item(s) from this collection and in which folders to place them.

In below example, collection "Beautiful" will NOT be exported into a "Beautiful" item (Export Type: None) but any Separate/Unique object or sub-collection inside it will be placed into folder "Rocks/Beautiful".

![collection export settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/collection_export.png?raw=true)

Each collection also stores item export settings for itself and for its unique/separate (see below) objects.

In below example, collection "Beautiful" stores export settings for both the "Rocks/Beautiful/Flat" and "Rocks/Beautiful/Slope" items.

![item settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/collection_item.png?raw=true)

## Objects

Objects (meshes, lights, pivots, etc.) by default are not exported into their own item but rather as part of the collection's item (when collection's export type is set to "Collection"). However when their export type is set to Separate or Unique, objects will generate their own item such that multiple object in a single collection can generate multiple items (all exported with the same collection's item settings).

- Export type tells whether object should be exported into an item with collection or every Separate object in the collection ("Collection"), with itself and other "Collection" objects in the collection ("Separate"), with itself only ("Unique") or ignored all together ("None").
- Path type tells how to name an exported Separate/Unique object

In below example both "Slope" and "Flat" objects are set to "Separate" export type while each "Pivot" object is set to "Collection". During export, this will lead both "Flat" and "Slope" objects to be exported with into their own "Rocks/Beautiful/Flat" and "Rocks/Beautiful/Slope" items with all 4 pivots. If "Flat" export type was set to "Unique" instead, it would be exported with none of the pivots.

![object export settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/object_export.png?raw=true)

## Meshes

Mesh-specific settings can allow hidding collider meshes or disabling physics of visible meshes. It can also help set triggers and spawn points for starts/finishes/checkpoints.

Make sure a mesh is selected and active to see the following:

![mesh settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/mesh.png?raw=true)

## Lights

Light-specific settings can allow modifying key parameters exported with the item(s).

Make sure a light is selected and active to see the following:

![light settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/light.png?raw=true)

## Materials

Material-specific settings can allow modifying visuals, physics, and gameplay property of exported items. And item can be composed of multiple materials and each material's property is modifyable in the material section.

Note that gameplay and color properties will only be editable when they would have an effect; else they will not be shown. Play with "Material" type to see which materias can accept a custom color or gameplay property.

![material settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/material.png?raw=true)

## Export

Once your are done setting up your items, it is time to export. To do so, select each "Separate"/"Unique" items you wish to export as well as at least 1 "Collection" item from each collection you wish to export and press the "Export Selection" button.
  
A good way to setup your workspace is to setup your entire scene's collections/objects such that you can then select it all (`A`) then click the export button and generate every items all at once.

In below example, objects "Slope" and "Mesh" are selected. The first one will create item "Rocks/Beautiful/Slope" which will contain 4 pivots. The second will create item "Rocks/MyLight" which will contain a mesh and a point light.

![export](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/export.png?raw=true)

## Copy settings

To copy export/item settings between collections/objects, select elements to paste settings to (hold `Ctrl`) and finish by selecting element to copy settings from (keep holding `Ctrl`), then click the appropriate copy button. Collection's selection is done by selecting any object within the collection.

In below example, item settings from "MyLight" collection will be copied into "Beautiful" and "MyCheckpoint" collection.

![copy settings](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/copy.png?raw=true)
