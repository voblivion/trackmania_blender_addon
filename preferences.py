import os

import bpy
from pathlib import Path
from bpy.types import (
    AddonPreferences,
)

from bpy.props import (
    StringProperty
)

class TrackmaniaAddonPreferences(AddonPreferences):
    bl_idname = __name__.split('.')[0]
    
    install_dir: StringProperty(
        name='Trackmania Install Directory',
        description='Where Trackmania and NadeoImporter are installed (usually: C:/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/games/Trackmania).',
        subtype='DIR_PATH',
        default=str(Path(os.environ['ProgramFiles(x86)'], 'Ubisoft/Ubisoft Game Launcher/games/Trackmania')),
    )
    
    user_dir: StringProperty(
        name='Trackmania User Directory',
        description='Where Trackmania saves user data (usually: C:/Users/<user>/Documents/Trackmania/Work/Items).',
        subtype='DIR_PATH',
        default=str(Path.home() / 'Documents/Trackmania'),
    )
    
    openplanet_dir: StringProperty(
        name='Openplanet user Directory',
        description='Where Openplanet saves user data (usually: C:/Users/<user>/OpenplanetNext). Only if you need to use default materials.',
        subtype='DIR_PATH',
        default=str(Path.home() / 'OpenplanetNext'),
    )
    
    author_name: StringProperty(
        name='Author Name',
        description='Author name used when exporting items.',
        default=os.getlogin(),
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'install_dir')
        layout.prop(self, 'user_dir')
        layout.prop(self, 'openplanet_dir')
        layout.prop(self, 'author_name')

def register():
    bpy.utils.register_class(TrackmaniaAddonPreferences)
    

def unregister():
    bpy.utils.unregister_class(TrackmaniaAddonPreferences)

    