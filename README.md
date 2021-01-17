# How to install

- Ensure blender version is 2.9 or above
- Download (zip / repository) into "%AppData%/Roaming/Blender Foundation/Blender/2.91/scripts/addons/"
- In blender: Edit > Preferences > Add-ons > Install > Select __init__.py file from downloaded files

# How to use

## Item

Any scene is considered an item in itself so 1 blender file can be exported into multiple items.

To edit item settings, in Object Mode open "Item" panel in "Trackmania" sidebar.

On the same panel you can them use "Export > Current Scene/Item" to export/import item into Trackmania.

If Item is a Waypoint, set its type : "Trackmania" sidebar > "Item" panel > "Other" section > Waypoint.  

## Mesh / Trigger

To create a new Mesh/Trigger, use action "Add > Trackmania > Add Mesh/Trigger" in top bar (Object mode only).

You can also create a standard blender mesh and edit it's type from "Mesh" panel in "Trackmania" sidebar.

## Spawn Point

For Waypoint items only.

A mesh type can also be set to "Spawn Point". When doing so, only position/orientation of object is considered during export.

Best is to create Spawn Point from "Add > Trackmania > Add Spawn Point" in top bar as it creates a model to easily visualize where car will spawn.

## Lights

Only Spot/Point lights can be exported, which you can create either through blender standard actions or through "Add > Trackmania" menu in top bar.

## Pivots

Add an empty object and set "Is Pivot" in: "Trackmania" sidebar > "Pivot" panel.

## Materials

If you want to use default TM materials, make sure you load material library ("Trackmania" sidebar > "Material Library" panel) then you can apply any of them to your meshes.
