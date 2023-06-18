import bpy
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

# HACK
from importlib import reload
all = reload(all)
copy = reload(copy)
icon = reload(icon)
item = reload(item)
mesh = reload(mesh)
mesh_params = reload(mesh_params)
nadeo_import = reload(nadeo_import)


operators = [
    all.SCENE_OT_TrackmaniaExportAll,
    icon.SCENE_OT_TrackmaniaExportIcon,
    item.SCENE_OT_TrackmaniaExportItem,
    copy.SCENE_OT_TrackmaniaItemCopy,
    copy.SCENE_OT_TrackmaniaItemPaste,
    mesh.SCENE_OT_TrackmaniaExportMesh,
    mesh_params.SCENE_OT_TrackmaniaExportMeshParams,
    nadeo_import.SCENE_OT_TrackmaniaNadeoImport,
]

def register():
    for operator in operators:
        bpy.utils.register_class(operator)

def unregister():
    for operator in operators[::-1]:
        bpy.utils.unregister_class(operator)
