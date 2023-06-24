from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
)


class COLLECTION_PG_TrackmaniaItem(PropertyGroup):
    bl_idname = 'COLLECTION_PG_TrackmaniaItem'
    
    export_type: EnumProperty(
        name='Export Type',
        items=(
            ('INHERIT', 'Inherit', 'Collection uses parent collection\'s export settings or None if collection is scene\'s main collection.'),
            ('NONE', 'None', 'Collection doesn\'t exported into any item and its direct child objects are not exported into any item.'),
            ('SINGLE', 'Single', 'Collection is exported into an unique item named after the collection and with all objects it contains.'),
            ('MULTIPLE', 'Multiple', 'Each mesh / light in the collection is exported into its own item. Pivots (empty objects) are shared.')
        ),
        default='INHERIT'
    )
    
    creates_folder: BoolProperty(
        name='Creates Folder',
        description='Whether or not this collection will participate in the folder hiearchy of exported items. When set, a folder named after the collection will be created inside parent collection\'s folder.',
        default=True
    )
    
    # Levitation
    ghost_mode: BoolProperty(
        name='Ghost Mode',
        description='Whether or not editor should ignore blocks/items when placing generated item or attempt to place it on them',
        default=False
    )
    fly_step: FloatProperty(
        name='Step',
        description='Increment by which cursor altitude is changed when scrolling with this item in hand',
        default=0
    )
    fly_offset: FloatProperty(
        name='Offset',
        description='Offset from virtual vertical grid defined by Fly Step',
        default=0
    )
    # Grid
    grid_horizontal_step: FloatProperty(
        name='Horizontal Step',
        description='Size of horizontal grid item can be placed on',
        default=0
    )
    grid_horizontal_offset: FloatProperty(
        name='Horizontal Offset',
        description='By how much item is offset when placed on its horizontal grid',
        default=0
    )
    grid_vertical_step: FloatProperty(
        name='Vertical Step',
        description='Size of vertical grid item can be placed on',
        default=0
    )
    grid_vertical_offset: FloatProperty(
        name='Vertical Offset',
        description='By how much item is offset when placed on its vertical grid',
        default=0
    )
    # Pivot
    pivot_manual_switch: BoolProperty(
        name='Manual Switch',
        description='Disables automatic pivot switch',
        default=False
    )
    pivot_automatic_snap: BoolProperty(
        name='Automatic Snap',
        description='Whether or not pivot snap distance is automatically decided by editor',
        default=True
    )
    pivot_snap_distance: FloatProperty(
        name='Snap Distance',
        description='Distance at which editor will try to snap item on another according to their pivot points',
        default=1,
        min=0
    )
    
    @property
    def pivot_snap_distance_raw(self):
        if self.pivot_automatic_snap:
            return -1
        return self.pivot_snap_distance
    
    # Miscellaneous
    waypoint_type: EnumProperty(
        name='Waypoint Type',
        description='Type of waypoint, None if not a waypoint',
        items=(
            ('NONE', 'None', ''),
            ('Start', 'Start', ''),
            ('Finish', 'Finish', ''),
            ('StartFinish', 'Multilap', ''),
            ('Checkpoint', 'Checkpoint', ''),
        ),
    )
    scale: FloatProperty(
        name='Scale',
        description='Scale applied to object before import',
        default=1,
        min=0.01
    )
    not_on_item: BoolProperty(
        name='Not On Item',
        description='Prevents exported item from being placed on another item',
        default=False
    )
    one_axis_rotation: BoolProperty(
        name='One Axis Rotation',
        description='Only allows rotating object on its Yaw axis',
        default=False
    )
    auto_rotation: BoolProperty(
        name='Auto Rotation',
        description='Rotates item according to surface it is placed on',
        default=False
    )
    # Icon
    def update_icon_settings(self, context):
        pass #TODO: bpy.ops.trackmania.render_icon(force_default_camera=True, save=False)
    
    icon_generate_camera: BoolProperty(
        name='Generate Camera',
        description='If set, will add a camera to the scene before generating Item\'s Icon.',
        default=True,
        update=update_icon_settings
    )
    icon_camera_pitch: FloatProperty(
        name='Camera Pitch',
        description='Pitch angle of default camera. Add your own camera to ignore.',
        default=45,
        update=update_icon_settings
    )
    icon_camera_yaw: FloatProperty(
        name='Camera Yaw',
        description='Yaw angle of camera. Add your own camera to ignore.',
        default=45,
        update=update_icon_settings
    )
    icon_generate_sun: BoolProperty(
        name='Generate Sun',
        description='If set, will add a sun to the scene before generating Item\'s Icon.',
        default=True,
        update=update_icon_settings
    )
    icon_sun_color: FloatVectorProperty(
        name='Sun Color',
        description='Color for generated Sun',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        default=(1, 1, 1),
        update=update_icon_settings
    )
    icon_sun_offset_pitch: FloatProperty(
        name='Sun Offset Pitch',
        description='By how much -relative to camera\'s pitch- sun\'s pitch is offset.',
        default=15,
        update=update_icon_settings
    )
    icon_sun_offset_yaw: FloatProperty(
        name='Sun Offset Yaw',
        description='By how much -relative to camera\'s yaw- sun\'s yaw is offset.',
        default=15,
        update=update_icon_settings
    )
