import bpy
from bpy.types import PropertyGroup
from bpy.props import (BoolProperty, EnumProperty, PointerProperty, StringProperty)
import pathlib
from ..utils import export

# HACK reload
import importlib
export = importlib.reload(export)


class MESH_PG_TrackmaniaMesh(PropertyGroup):
    bl_idname = 'MESH_PG_TrackmaniaMesh'
    
    mesh_type: EnumProperty(
        name='Mesh Type',
        items=(
            ('MESH', 'Mesh', 'A mesh be collidable and/or visible to player'),
            ('TRIGGER', 'Trigger', 'A trigger to be used by waypoint item'),
            ('SPAWN', 'Spawn', 'Waypoint spawn point'),
        )
    )
    
    is_visible: BoolProperty(
        name='Is Visible',
        default=True
    )
    
    is_collidable: BoolProperty(
        name='Is Collidable',
        default=True
    )
    
    @property
    def render_on_icon(self):
        return self.mesh_type == 'MESH' and (self.is_visible or not self.is_collidable)
    
    def get_export_name(self, base_name):
        if self.mesh_type == 'SPAWN':
            return '_socket_start'
        elif self.mesh_type == 'TRIGGER':
            return '_trigger_' + base_name
        elif not self.is_visible and not self.is_collidable:
            return '_skip_' + base_name
        elif not self.is_visible:
            return '_notvisible_' + base_name
        elif not self.is_collidable:
            return '_notcollidable_' + base_name
        else:
            return base_name

def register():
    bpy.utils.register_class(MESH_PG_TrackmaniaMesh)
    bpy.types.Mesh.trackmania_mesh = PointerProperty(type=MESH_PG_TrackmaniaMesh)

def unregister():
    bpy.utils.unregister_class(MESH_PG_TrackmaniaMesh)
    del bpy.types.Mesh.trackmania_mesh
