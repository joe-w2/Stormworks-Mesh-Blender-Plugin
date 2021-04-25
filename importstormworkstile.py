import os
import re
import xml.etree.ElementTree as ET
from typing import Set

import numpy as np
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy_types import Operator

from .importstormworksmesh import ImportStormworksMesh
from .tile import Tile


class ImportStormworksTile(Operator, ImportHelper):
    """Import Stormworks Tile"""

    bl_idname = "stormworks_tile_importer.tile_data"
    bl_label = "Import Tile"

    filename_ext = ".xml"

    filter_glob: StringProperty(
        default="*.xml",
        options={"HIDDEN"},
        maxlen=255,
    )

    @staticmethod
    def read_tile(filepath: str, meshfolder: str) -> None:
        with open(filepath, "r") as file:
            xmlstring = file.read()

        xmlstring = re.sub(r"(\d\d=)", r"t\1", xmlstring)
        parsedContent = ET.fromstring(xmlstring)

        tile = Tile(parsedContent)

        for mesh in tile.meshes:
            filepath = os.path.join(meshfolder, mesh.filename)
            vertices, faces, submeshes = ImportStormworksMesh.read_mesh(filepath)

            for vertex in vertices:
                matrix = mesh.transformation.matrix

                pos = matrix.transpose().dot(np.array([vertex.x, vertex.y, vertex.z, 1]))
                pos2 = matrix.transpose().dot(np.array([vertex.nx, vertex.ny, vertex.nz, 1]))

                vertex.x, vertex.y, vertex.z, _ = *pos,
                vertex.nx, vertex.ny, vertex.nz, _ = *pos2,
                vertex.x *= -1

            ImportStormworksMesh.add_mesh(mesh.mesh_id, vertices, faces, submeshes)

    @staticmethod
    def import_tile(context, filepath: str) -> None:
        print(f"Importing {filepath}")
        ImportStormworksTile.read_tile(filepath, context.preferences.addons[__package__].preferences.meshfolderpath)
        print(f"Finished Importing")

    def execute(self, context) -> Set[str]:
        ImportStormworksTile.import_tile(context, self.filepath)
        return {"FINISHED"}
