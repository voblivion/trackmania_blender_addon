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
    bl_idname = 'Trackmania'
    
    install_dir: StringProperty(
        name='Trackmania Install Directory',
        description='Where Trackmania and NadeoImporter are installed (usually: C:/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/games/Trackmania)',
        subtype='DIR_PATH',
        default=str(Path(os.environ['ProgramFiles(x86)'], 'Ubisoft/Ubisoft Game Launcher/games/Trackmania'))
    )
    
    user_dir: StringProperty(
        name='Trackmania User Directory',
        description='Where Trackmania saves user data (usually: <user>/Documents/Trackmania/Work/Items)',
        subtype='DIR_PATH',
        default=str(Path.home() / 'Documents/Trackmania')
    )
    
    author_name: StringProperty(
        name='Author Name',
        description='Author name used when exporting items',
        default=''
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'install_dir')
        layout.prop(self, 'user_dir')
        layout.prop(self, 'author_name')
        

classes = (
    TrackmaniaAddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    