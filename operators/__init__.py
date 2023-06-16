from . import copy, icon, item, mesh, mesh_params, nadeo_import, export_selection

import importlib
copy = importlib.reload(copy)
icon = importlib.reload(icon)
item = importlib.reload(item)
mesh = importlib.reload(mesh)
mesh_params = importlib.reload(mesh_params)
nadeo_import = importlib.reload(nadeo_import)
export_selection = importlib.reload(export_selection)

modules = [copy, icon, item, mesh, mesh_params, nadeo_import, export_selection]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in modules[::-1]:
        module.unregister()
