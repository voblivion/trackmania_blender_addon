import bpy
# primary
from . import all
from . import copy
from . import icon
from . import item
from . import mesh
from . import mesh_params
from . import nadeo_import
from .all import (SCENE_OT_TrackmaniaExportAll,)
from .copy import (SCENE_OT_TrackmaniaItemCopy, SCENE_OT_TrackmaniaItemPaste,)
from .icon import (SCENE_OT_TrackmaniaExportIcon,)
from .item import (SCENE_OT_TrackmaniaExportItem,)
from .mesh import (SCENE_OT_TrackmaniaExportMesh,)
from .mesh_params import (SCENE_OT_TrackmaniaExportMeshParams,)
from .nadeo_import import (SCENE_OT_TrackmaniaNadeoImport,)
# secondary
from . import tools
from .tools import (
    SCENE_OT_SelectUVLayer,
    SCENE_OT_CreateUVLayer,
    SCENE_OT_TrackmaniaImportDefaultMaterials,
    SCENE_OT_TrackmaniaCreateCustomMaterial,
    SCENE_OT_TrackmaniaAddDefaultMaterial,
    SCENE_OT_TrackmaniaCreateMissingUVLayers,
    SCENE_OT_TrackmaniaRemoveExtraUVLayers,
    SCENE_OT_TrackmaniaPrefixItem,
)
# special
from ..properties.material import _get_trackmania_materials

# HACK
from importlib import reload
all = reload(all)
copy = reload(copy)
icon = reload(icon)
item = reload(item)
mesh = reload(mesh)
mesh_params = reload(mesh_params)
nadeo_import = reload(nadeo_import)
tools = reload(tools)


operators = [
    all.SCENE_OT_TrackmaniaExportAll,
    icon.SCENE_OT_TrackmaniaExportIcon,
    item.SCENE_OT_TrackmaniaExportItem,
    copy.SCENE_OT_TrackmaniaItemCopy,
    copy.SCENE_OT_TrackmaniaItemPaste,
    mesh.SCENE_OT_TrackmaniaExportMesh,
    mesh_params.SCENE_OT_TrackmaniaExportMeshParams,
    nadeo_import.SCENE_OT_TrackmaniaNadeoImport,
    
    tools.SCENE_OT_SelectUVLayer,
    tools.SCENE_OT_CreateUVLayer,
    tools.SCENE_OT_TrackmaniaImportDefaultMaterials,
    tools.SCENE_OT_TrackmaniaCreateCustomMaterial,
    tools.SCENE_OT_TrackmaniaAddDefaultMaterial,
    tools.SCENE_OT_TrackmaniaCreateMissingUVLayers,
    tools.SCENE_OT_TrackmaniaRemoveExtraUVLayers,
    tools.SCENE_OT_TrackmaniaPrefixItem,
]

def _get_custom_material_identifiers(self, context):
    return [(identifier, identifier, '') for identifier in _get_trackmania_materials(context) if 'Custom' in identifier]

def register():
    bpy.types.Scene.custom_material = bpy.props.EnumProperty(
        items=_get_custom_material_identifiers,
        name='Custom Material',
        default=0,
    )
    bpy.types.Scene.default_material = bpy.props.StringProperty(default='')
    bpy.types.Scene.current_item_prefix = bpy.props.IntProperty(default=99)
    
    for operator in operators:
        bpy.utils.register_class(operator)

def unregister():
    for operator in operators[::-1]:
        bpy.utils.unregister_class(operator)
