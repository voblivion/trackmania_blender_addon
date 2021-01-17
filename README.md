# How to install

- Ensure blender version is 2.9 or above
- Ensure Trackmania2020 and NadeoImporter are installed (https://doc.trackmania.com/nadeo-importer/)
- Download (zip / repository) into "%AppData%/Roaming/Blender Foundation/Blender/2.91/scripts/addons/"
- In blender: Edit > Preferences > Add-ons > Install > Select __init__.py file from downloaded files

# How to use

## Item

Any scene is considered an item in itself so 1 blender file can be exported into multiple items. Item will be exported according to scene's name with forward slashes ('/') taken into account.


Settings :
- sidebar > Trackmania > Item


Export :
- sidebar > Trackmania > Item > Export > Current Scene/Item

## Mesh / Trigger

Create :
- top bar > Add > Trackmania > Add Mesh/Trigger

Settings :
- sidebar > Trackmania > Mesh

## Spawn Point

For Waypoint items only. Only position and orientation of mesh are taken into account during export.

Create :
- top bar > Add > Trackmania > Add Spawn Point

## Lights

Only Spot/Point lights can be exported.

Create :
- top bar > Add > Trackmania > Add Spot/Point Light

## Pivots

Create :
- top bar > Add > Trackmania > Add Pivot

## Materials

Define how blender material will be translated into TM materials during export.

Settings :
- side pannels > Material Properties > Trackmania Material

Load default materials library :
- sidebar > Trackmania > Material Library > Load Material Library
