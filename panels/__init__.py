import bpy
from . import export
from . import item
from . import light
from . import material
from . import mesh
from . import uv

# HACK
from importlib import reload
export = reload(export)
item = reload(item)
light = reload(light)
material = reload(material)
mesh = reload(mesh)
uv = reload(uv)

panels = [
    export.VIEW3D_PT_TrackmaniaExport,
    item.VIEW3D_PT_TrackmaniaItem,
    item.VIEW3D_PT_TrackmaniaItemLevitation,
    item.VIEW3D_PT_TrackmaniaItemGrid,
    item.VIEW3D_PT_TrackmaniaItemPivot,
    item.VIEW3D_PT_TrackmaniaItemMiscellaneous,
    item.VIEW3D_PT_TrackmaniaItemIcon,
    light.PROPERTIES_PT_TrackmaniaLight,
    light.VIEW3D_PT_TrackmaniaLight,
    material.MATERIAL_PT_TrackmaniaMaterial,
    mesh.PROPERTIES_PT_TrackmaniaMesh,
    mesh.VIEW3D_PT_TrackmaniaMesh,
    uv.VIEW3D_PT_TrackmaniaMaterials,
]

def register():
    for panel in panels:
        bpy.utils.register_class(panel)

def unregister():
    for panel in panels[::-1]:
        bpy.utils.unregister_class(panel)
