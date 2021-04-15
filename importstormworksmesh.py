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
        bytestring, (vertex_count,) = ImportStormworksMesh._get(bytestring, "H")
        bytestring = ImportStormworksMesh._skip(bytestring, 4)

        vertices = []

        for i in range(vertex_count):
            bytestring, position = ImportStormworksMesh._get(bytestring, "fff")

            bytestring, colour = ImportStormworksMesh._get(bytestring, "BBBB")

            bytestring, normal = ImportStormworksMesh._get(bytestring, "fff")

            vertex = Vertex(*position, *colour, *normal)
            vertices.append(vertex)

        bytestring, (triangle_count,) = ImportStormworksMesh._get(bytestring, "I")
        triangle_count = triangle_count // 3

        faces = []

        for i in range(triangle_count):
            bytestring, points = ImportStormworksMesh._get(bytestring, "HHH")

            faces.append(points)

        return vertices, faces

    @staticmethod
    def add_mesh(name, vertices: List[Vertex], faces: List[Tuple[int, int, int]]) -> None:
        mesh_data = bpy.data.meshes.new(name)

        vertices_as_tuple_list = list(map(lambda a: (a.x, a.y, a.z), vertices))

        mesh_data.from_pydata(vertices_as_tuple_list, [], faces)
        mesh_data.update()

        colour_layer = mesh_data.vertex_colors.new(name="Colour Layer")

        for poly in mesh_data.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = mesh_data.loops[loop_index].vertex_index

                colour_layer.data[loop_index].color = vertices[vertex_index].r / 255, vertices[vertex_index].g / 255, \
                                                      vertices[vertex_index].b / 255, vertices[vertex_index].a / 255

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
