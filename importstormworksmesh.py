import struct
from typing import List, Tuple, Set, Any

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy_types import Operator

from .vertex import Vertex


class ImportStormworksMesh(Operator, ImportHelper):
    """Import Stormworks Mesh"""

    bl_idname = "stormworks_mesh_importer.mesh_data"
    bl_label = "Import Mesh"

    filename_ext = ".mesh"

    filter_glob: StringProperty(
        default="*.mesh",
        options={"HIDDEN"},
        maxlen=255,
    )

    @staticmethod
    def _get(bytestring: bytes, structure: str) -> Tuple[bytes, Tuple[Any]]:
        size = struct.calcsize(structure)

        a, bytestring = bytestring[:size], bytestring[size:]

        return bytestring, struct.unpack(structure, a)

    @staticmethod
    def _skip(bytestring: bytes, size: int) -> bytes:
        return bytestring[size:]

    @staticmethod
    def read_mesh(filepath: str) -> Tuple[List[Vertex], List[Tuple[int, int, int]]]:
        with open(filepath, "rb") as file:
            bytestring = file.read()

        assert bytestring.startswith(b"mesh\x07\x00\x01\x00") and bytestring.endswith(b"\x00\x00")

        bytestring = ImportStormworksMesh._skip(bytestring, 8)
        bytestring, (vertexCount,) = ImportStormworksMesh._get(bytestring, "H")
        bytestring = ImportStormworksMesh._skip(bytestring, 4)

        vertices = []

        for i in range(vertexCount):
            bytestring, position = ImportStormworksMesh._get(bytestring, "fff")

            bytestring, colour = ImportStormworksMesh._get(bytestring, "BBBB")

            bytestring, normal = ImportStormworksMesh._get(bytestring, "fff")

            vertex = Vertex(*position, *colour, *normal)
            vertices.append(vertex)

        bytestring, (triangleCount,) = ImportStormworksMesh._get(bytestring, "I")
        triangleCount = triangleCount // 3

        faces = []

        for i in range(triangleCount):
            bytestring, points = ImportStormworksMesh._get(bytestring, "HHH")

            faces.append(points)

        return vertices, faces

    @staticmethod
    def add_mesh(name, vertices: List[Vertex], faces: List[Tuple[int, int, int]]) -> None:
        mesh_data = bpy.data.meshes.new(name)

        verticesAsTupleList = list(map(lambda a: (a.x, a.y, a.z), vertices))

        mesh_data.from_pydata(verticesAsTupleList, [], faces)
        mesh_data.update()

        colourLayer = mesh_data.vertex_colors.new(name="Colour Layer")

        for poly in mesh_data.polygons:
            for loopIndex in poly.loop_indices:
                vertexIndex = mesh_data.loops[loopIndex].vertex_index
                colourLayer.data[loopIndex].color = vertices[vertexIndex].r / 255, vertices[vertexIndex].g / 255, \
                                                    vertices[vertexIndex].b / 255, vertices[vertexIndex].a

        obj = bpy.data.objects.new(mesh_data.name, mesh_data)

        scene = bpy.context.scene
        scene.collection.objects.link(obj)

    @staticmethod
    def import_mesh(context, filepath: str) -> None:
        print(f"Importing {filepath}")
        vertices, faces = ImportStormworksMesh.read_mesh(filepath)
        print(f"Finished Importing")

        ImportStormworksMesh.add_mesh("Imported Mesh", vertices, faces)

    def execute(self, context) -> Set[str]:
        ImportStormworksMesh.import_mesh(context, self.filepath)
        return {"FINISHED"}
