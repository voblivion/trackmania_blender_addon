import bpy
import re
import functools
from pathlib import Path
from bpy.types import (
    Panel,
    PropertyGroup,
)
from bpy.props import (
    EnumProperty,
    FloatVectorProperty,
    PointerProperty
)

class TmMaterial():
    def __init__(self, name):
        self.name = name
        self.allows_color = name[:6] == 'Custom'
        self.needs_base_material_uv = False
        self.needs_lightmap_uv = False

@functools.lru_cache(maxsize=1)
def get_tm_materials(context):
    path = Path(context.preferences.addons['Trackmania'].preferences.install_dir, 'NadeoImporterMaterialLib.txt')
    file = open(path)
    
    tm_materials = {}
    tm_material = None
    lines = file.readlines()
    for line in lines:
        tokens = [token.strip() for token in re.split('\(|\)|,', line)]
        if len(tokens) < 2:
            continue
        if tokens[0] == 'DMaterial':
            tm_materials[tokens[1]] = TmMaterial(tokens[1])
            tm_material = tm_materials[tokens[1]]
        elif tokens[0] == 'DUvLayer':
            if tokens[1] == 'BaseMaterial':
                tm_material.needs_base_material_uv = True
            elif tokens[1] == 'Lightmap':
                tm_material.needs_lightmap_uv = True
    return tm_materials
    

class MATERIAL_PG_TrackmaniaMaterial(PropertyGroup):
    bl_idname = 'MATERIAL_PG_TrackmaniaMaterial'
    
    def get_tm_materials(self, context):
        return [(name, name, '') for name in get_tm_materials(context)]
    
    name: EnumProperty(
        items=get_tm_materials,
        name='Link Name',
        description='A Trackmania material supported by NadeoImporter'
    )
    
    color: FloatVectorProperty(
        name='Color',
        description='Color for Custom materials',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        default=(1, 1, 1)
    )

class MATERIAL_PT_TrackmaniaMaterial(Panel):
    bl_idname = 'MATERIAL_PT_TrackmaniaMaterial'
    bl_label = 'Trackmania Material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'Trackmania'
    
    @classmethod
    def poll(cls, context):
        return context.material is not None
    
    def draw(self, context):
        layout = self.layout
        trackmania_settings = context.material.trackmania_material
        
        layout.prop(trackmania_settings, 'name')
        layout.prop(trackmania_settings, 'color')
    

classes = (
    MATERIAL_PG_TrackmaniaMaterial,
    MATERIAL_PT_TrackmaniaMaterial,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.trackmania_material = PointerProperty(type=MATERIAL_PG_TrackmaniaMaterial)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Material.trackmania_material

