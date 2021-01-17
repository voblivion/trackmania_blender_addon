# How to install

- Ensure blender version is 2.9 or above
- Ensure Trackmania2020 and NadeoImporter are installed (https://doc.trackmania.com/nadeo-importer/)
- Download ZIP from repository (github > green "Code" button > Download ZIP)
- Install into blender: Edit > Preferences > Add-ons > Install > Select downloaded zip file
- Change Author Name to yours: Edit > Preferences > Add-ons > Trackmania > Author Name

Since this addon is still heavily WIP, you can also clone this repository into Blender's addons folders too keep it up-to-date more easily (make sure you then Install it into blender through \_\_init\_\_.py file).


This repository also includes textures for default materials. When dowloading zip version of it they won't be included. Make sure you replace them with your own if you want to use that feature (or install it through git clone as explained above).

# How to use

## Item

Any scene is considered an item in itself so 1 blender file can be exported into multiple items. Item will be exported according to scene's name with forward slashes ('/') taken into account. If you don't want a scene to be exported as an Item (for instance if your scene is a test one) you can un-check all export checkboxes (see below).


Settings :
- sidebar > Trackmania > Item


Export :
- sidebar > Trackmania > Item > Export > Current Scene/Item

## Mesh / Trigger

Create :
- top bar > Add > Trackmania > Add Mesh/Trigger

Settings :
- sidebar > Trackmania > Mesh

_Any mesh created through standard blender buttons will also be exported. You can change their type through the same settings panel._

## Spawn Point

Must be unique. For Waypoint items only. Only position and orientation of mesh are taken into account during export.

Create :
- top bar > Add > Trackmania > Add Spawn Point

_Any mesh (whose trackmania type is "Spawn") created through standard blender buttons will also be exported as spawn point. See Mesh/Trigger settings above._

## Lights

Only Spot/Point lights can be exported.

Create :
- top bar > Add > Trackmania > Add Spot/Point Light

_Any spot/point light created through standard blender buttons will also be exported_

## Pivots

They are exported in alphabetical order!

Create :
- top bar > Add > Trackmania > Add Pivot

_Any empty blender object can also be set pivot: sidebar > Trackmania > Pivot > Is Pivot_

## Materials

Define how blender material will be translated into TM materials during export.

Settings :
- side pannels > Material Properties > Trackmania Material

You can create all the material you want, then setup how you want them exported. You can also use default materials (includes roads, platforms, and deco-hill) by loading it:
- sidebar > Trackmania > Material Library > Load Material Library

_This part is still WIP and some default materials may be exported with inadequate colors. In addition you will have to add the textures yourself into the addon because they are not included in the ZIP file._
