import bpy
from . import item
from . import material
from . import mesh

# HACK
from importlib import reload
item = reload(item)
material = reload(material)
mesh = reload(mesh)

property_groups = [
    item.COLLECTION_PG_TrackmaniaItem,
    material.MATERIAL_PG_TrackmaniaMaterial,
    mesh.MESH_PG_TrackmaniaMesh,
]

def register():
    for property_group in property_groups:
        bpy.utils.register_class(property_group)
    
    bpy.types.Collection.trackmania_item = bpy.props.PointerProperty(type=item.COLLECTION_PG_TrackmaniaItem)
    bpy.types.Material.trackmania_material = bpy.props.PointerProperty(type=material.MATERIAL_PG_TrackmaniaMaterial)
    bpy.types.Mesh.trackmania_mesh = bpy.props.PointerProperty(type=mesh.MESH_PG_TrackmaniaMesh)

def unregister():
    del bpy.types.Mesh.trackmania_mesh
    del bpy.types.Material.trackmania_material
    del bpy.types.Collection.trackmania_item
    
    for property_group in property_groups[::-1]:
        bpy.utils.unregister_class(property_group)
