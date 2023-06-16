import bpy
from bpy.types import PropertyGroup
from bpy.props import (EnumProperty, FloatVectorProperty, PointerProperty)
from ..utils import tm

# HACK reload
import importlib
tm = importlib.reload(tm)


class MATERIAL_PG_TrackmaniaMaterial(PropertyGroup):
    bl_idname = 'MATERIAL_PG_TrackmaniaMaterial'
    
    def get_tm_materials(self, context):
        return [(name, name, '') for name in tm.get_tm_materials(context)]
    
    material: EnumProperty(
        items=get_tm_materials,
        name='Material',
        description='A Trackmania material supported by NadeoImporter'
    )
    
    gameplay: EnumProperty(
        items=[(item[0], item[0], item[1]) for item in tm.gameplay_ids],
        name='Gameplay',
        description='Setting a value different than None will add a special gameplay effect to the surface, like activating free wheeling or slow motion modes. Some of those gameplay effects such as Turbo or ReactorBoost are "oriented": the direction of this effect is automatically the local z-axis of the item.',
        default='None'
    )
    
    physics: EnumProperty(
        items=[(item[0], item[0], item[1]) for item in tm.physics_ids],
        name='Physics',
        description='Overrides the way the cars will interact physically with the surface. You should not overuse this feature because it is usually a bad idea (for gameplay and fun) to have a surface looking like grass but behaving like dirt.',
        default='Default'
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

def register():
    bpy.utils.register_class(MATERIAL_PG_TrackmaniaMaterial)
    bpy.types.Material.trackmania_material = PointerProperty(type=MATERIAL_PG_TrackmaniaMaterial)

def unregister():
    bpy.utils.unregister_class(MATERIAL_PG_TrackmaniaMaterial)
    del bpy.types.Material.trackmania_material

