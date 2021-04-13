from bpy.props import StringProperty
from bpy_types import AddonPreferences

if "bpy" in locals():
    import importlib

    importlib.reload(importstormworkstile)
    importlib.reload(exportstormworksmesh)
    importlib.reload(importstormworksmesh)
    importlib.reload(importstormworksblock)

import bpy

from . import importstormworkstile
from . import exportstormworksmesh
from . import importstormworksmesh
from . import importstormworksblock


class StormworksImportExportAddonPreferences(AddonPreferences):
    bl_idname = __package__

    meshfolderpath: StringProperty(
        name="Mesh Root Folder",
        description="Only .blend files two levels below this folder will be listed.",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "meshfolderpath")


def menu_func_import(self, context):
    self.layout.operator(importstormworksmesh.ImportStormworksMesh.bl_idname, text="Stormworks Mesh (.mesh)")
    self.layout.operator(importstormworkstile.ImportStormworksTile.bl_idname, text="Stormworks Tile (.xml)")
    self.layout.operator(importstormworksblock.ImportStormworksBlock.bl_idname, text="Stormworks Block (.xml)")


def menu_func_export(self, context):
    self.layout.operator(exportstormworksmesh.ExportStormworksMesh.bl_idname, text="Stormworks Mesh (.mesh)")


def register():
    bpy.utils.register_class(StormworksImportExportAddonPreferences)

    bpy.utils.register_class(importstormworksmesh.ImportStormworksMesh)
    bpy.utils.register_class(importstormworkstile.ImportStormworksTile)
    bpy.utils.register_class(importstormworksblock.ImportStormworksBlock)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    bpy.utils.register_class(exportstormworksmesh.ExportStormworksMesh)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(StormworksImportExportAddonPreferences)

    bpy.utils.unregister_class(importstormworksmesh.ImportStormworksMesh)
    bpy.utils.unregister_class(importstormworkstile.ImportStormworksTile)
    bpy.utils.unregister_class(importstormworksblock.ImportStormworksBlock)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    bpy.utils.unregister_class(exportstormworksmesh.ExportStormworksMesh)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


bl_info = {
    "name": "Import-Export Stormworks Mesh",
    "description": "Adds support for the import and export of Stormworks .mesh files.",
    "blender": (2, 80, 0),
    "category": "Import-Export",
    "author": "WALL-E#7332",
    "location": "File > Import > Stormworks Mesh",
}

if __name__ == "__main__":
    register()
