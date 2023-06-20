import bpy
from bpy.types import PropertyGroup
from bpy.props import (BoolProperty, EnumProperty, FloatVectorProperty, PointerProperty)

import functools
import pathlib
import re

from ..utils import preferences
from ..utils import materials as material_utils

# HACK
from importlib import reload
preferences = reload(preferences)


@functools.lru_cache(maxsize=1)
def _get_trackmania_materials(context):
    install_dir = preferences.get(context).install_dir
    filepath = pathlib.Path(install_dir) / 'NadeoImporterMaterialLib.txt'

    return material_utils.get_trackmania_materials(filepath)

class MATERIAL_PG_TrackmaniaMaterial(PropertyGroup):
    bl_idname = 'MATERIAL_PG_TrackmaniaMaterial'

    def _get_identifiers(self, context):
        return [(identifier, identifier, '') for identifier in _get_trackmania_materials(context)]

    @property
    def needs_base_material_uv(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].needs_base_material_uv

    @property
    def needs_lightmap_uv(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].needs_lightmap_uv

    identifier: EnumProperty(
        items=_get_identifiers,
        name='Identifier',
        description='A Trackmania material supported by NadeoImporter.',
        default=0,
    )

    physics: EnumProperty(
        items=[(item[0], item[0], item[1]) for item in material_utils.get_physics_ids()],
        name='Physics',
        description='Overrides the way the cars will interact physically with the surface. You should not overuse this feature because it is usually a bad idea (for gameplay and fun) to have a surface looking like grass but behaving like dirt.',
        default='Default'
    )

    @property
    def can_customize_gameplay(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].can_customize_gameplay

    gameplay: EnumProperty(
        items=[(item[0], item[0], item[1]) for item in material_utils.get_gameplay_ids()],
        name='Gameplay',
        description='Setting a value different than None will add a special gameplay effect to the surface, like activating free wheeling or slow motion modes. Some of those gameplay effects such as Turbo or ReactorBoost are "oriented": the direction of this effect is automatically the local z-axis of the item.',
        default='None'
    )

    @property
    def can_customize_color(self):
        trackmania_materials = _get_trackmania_materials(bpy.context)
        return self.identifier in trackmania_materials and trackmania_materials[self.identifier].can_customize_color
    
    def _update_color(self, context):
        node_tree = context.material.node_tree
                
        # trackmania_color = material.node_tree.nodes.new('RGB', label='Trackmania Color')
    
    color: FloatVectorProperty(
        name='Color',
        description='Color for Custom materials',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        default=(1, 1, 1),
        update=_update_color,
    )