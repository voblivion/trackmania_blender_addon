# Bug reporting & Feature suggestions
- Report issues through github interface (top bar)
- Feel free to suggest any feature/improvement in the form of a pull-request or via email (voblivion <at> hotmail <dot> fr)

# How to install

- Ensure blender version is 3.5 or above
- Ensure Trackmania2020 and NadeoImporter are installed (https://doc.trackmania.com/nadeo-importer/)
- Download latest release (see "Releases" section on the right)
- Install into blender: `Edit > Preferences > Add-ons > Install > Select downloaded release archive`
- Change Author Name to yours: Edit > Preferences > Add-ons > Trackmania > Author Name

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/preferences.png?raw=true)

Since this addon is still WIP, you can also clone this repository into Blender's addons folders to keep it up-to-date more easily (make sure you then Install it into blender through \_\_init\_\_.py file).

# How to use

## Collection

Select a collection in Blender's `Outliner`.

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/collection.png?raw=true)

Each Blender collection allows controlling item export settings for its child objects (meshes and lights). While this makes initial export more tedious (copy/pasting settings can help, see below), this allows for easier later update of exported items.

When collection's export type is set to "Single", all of its objects (meshes, lights, and empty objects) will be exported into a single trackmania item. This is useful for items such as checkpoints or lights which require multiple meshes to function.

When collection's export type is set to "Multiple", each of its object (meshes and lights) is exported as its own trackmania item (empty objects are still shared, see below). This is useful for simple objects which don't require

Collection's item export settings can be copied from and pasted to. This allows sharing settings between similar items more easily.

## Meshes

Mesh settings allow controlling the type of mesh (Mesh, Trigger, Spawn point) as well as the visibility/physic of exported mesh.

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/mesh.png?raw=true)

Tip: you can link the same meshes and lights to multiple collections so they are exported to multiple items but you only ever need to modify 1 of them. To do so, select items you wish to share and press `Shift + M`.

## Lights

Light settings allow controlling how lights are exported into items. Those are original Blender attributes grouped so it is easier to know which ones will affect the game.

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/light.png?raw=true)

## Pivots

Controlling item pivots is done by adding empty objects. When collection's export type is set to "Multiple", meshes and lights in the collection will share every pivot in the same collection.

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/pivot.png?raw=true)

## Materials

Material export settings can be changed in the material properties under the `Trackmania` section.

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/material.png?raw=true)

Note that some settings (Gameplay and Color) may appear/disappear as you update the material identifier. This is because trackmania doesn't support overriding gameplay and color properties for every material.

## Export

Once your are done setting up your items, it is time to export. Select objects you wish to export (`A` in `3D View` to select all) and press the export button.

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/export.png?raw=true)

Note that the exporter will export based on your collections' item export settings:
- Every "Single" export-type collection containing a selected object will be exported into its own item (with other objects from the collection, selected or not).
- Every selected object from a "Multiple" export-type collection will be exported into its own item (with pivots, selected or not).


You can also perform partial exports (icon, mesh, mesh params, item, nadeo import) or do full export by binding a shortcut to one of the following operators:
- trackmania.export_icon (exports the `.tga` icon)
- trackmania.export_mesh (exports the `.fbx` mesh)
- trackmania.export_mesh_params (exports the `.MeshParams.xml` file)
- trackmania.export_item (exports the `.Item.xml` file)
- trackmania.nadeo_import (calls nadeo importer on generated `.Item.xml` file)
- trackmania.export_all (calls all previous export/nadeo_import operators)

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/shortcut.png?raw=true)

## Tools

![collection](https://github.com/voblivion/trackmania_blender_addon/blob/main/doc/tools.png?raw=true)

Remember that every tool operator can be bound to your desired shortcut (see above).

### UV

- "Select \<Name\> Layer" (`uv.select_layer`): selects \<Name\> UV layer on selected meshes, so you can quickly switch between meshes to edit their UVs.
- "Create \<Name\> Layer" (`uv.create_layer`): creates \<Name\> UV layer on selected meshes which do not yet own a layer with this <Name>.
- "Create Missing Layers" (`trackmania.create_missing_uv_layers`): for each selected meshes, goes through materials and ensure their required UV layers (BaseMaterial and/or Lightmap) are present.
- "Remove Extra Layers" (`trackmania.remove_extra_uv_layers`): for each selected meshes, remove UV layers which are not needed for any of the mesh's materials.

### Material

- "Import Default Materials" (`trackmania.import_default_materials`): imports default materials and their textures ; this assumes you extracted `Textures` and `Textures_BlockCustom` with OpenPlanet beforehand. The script with attempt to find the best texture for each trackmania material that can be exported, based on rules in `<trackmania 2020 blender toolbox>/utils/default_textures.ini`. You can edit this file if you figure wrong textures are chosen.
- "Create Custom Material" (`trackmania.create_custom_material`): creates a custom material based on selected custom trackmania material type. This tool will setup material's shader nodes such that editing material's color will affect rendering in blender in a similar way it does in Trackmania.
- "Add Default Material To Objects" (`trackmania.add_default_material`): adds selected default material to each selected object which doesn't have any material.

### Object / Collection

- "Rename With Prefix" (`trackmania.prefix_rename`): renames active object/collection with current prefix, and decrements number in current prefix. Current prefix must contain exactly one number for this tool to function.
- "Set Trigger" (`trackmania.set_trigger`): makes each selected mesh a trigger (in regard to trackmania export settings). Also makes those meshes use the `TrackmaniaTrigger` to make it easier editting item's trigger and visual at the same time. 
