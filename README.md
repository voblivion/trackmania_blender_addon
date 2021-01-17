# How to install

- Ensure blender version is 2.9 or above
- Ensure Trackmania2020 and NadeoImporter are installed (https://doc.trackmania.com/nadeo-importer/)
- Download zip from repository (github > green "Code" button > Download ZIP)
- Load in blender: Edit > Preferences > Add-ons > Install > Select downloaded zip file
- Change Author Name to yours: Edit > Preferences > Add-ons > Trackmania > Author Name

Since this addon is still heavily WIP, you can also clone this repository into Blender's addons folders too keep it up-to-date more easily (make sure you also Install it through \_\_init\_\_.py file).


This repository also includes textures for default materials. When dowloading zip version of it they won't be included. Make sure you replace them with your own if you want to use that feature (or install it through git clone as explained above).

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

They are exported in alphabetical order!

Create :
- top bar > Add > Trackmania > Add Pivot

## Materials

Define how blender material will be translated into TM materials during export.

Settings :
- side pannels > Material Properties > Trackmania Material

Load default materials library :
- sidebar > Trackmania > Material Library > Load Material Library
