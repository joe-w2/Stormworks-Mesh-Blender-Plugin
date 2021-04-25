import struct
from typing import Set

import bmesh
import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper


class ExportStormworksMesh(Operator, ExportHelper):
    """Export Stormworks Mesh"""

    bl_idname = "stormworks_mesh_exporter.mesh_data"
    bl_label = "Export Mesh"

    filename_ext = ".mesh"

    filter_glob: StringProperty(
        default="*.mesh",
        options={"HIDDEN"},
        maxlen=255,
    )

    @staticmethod
    def _put(bytestring: bytes, structure: str, *values: object) -> bytes:
        packed_bytes = struct.pack(structure, *values)

        return bytestring + packed_bytes

    @staticmethod
    def _write(bytestring: bytes, bytes_to_write: bytes) -> bytes:
        return bytestring + bytes_to_write

    @staticmethod
    def write_mesh(filepath: str) -> None:
        obj = bpy.context.object

        assert obj and obj.type == "MESH"

        mesh = obj.data

        bm = bmesh.new()
        bm.from_mesh(mesh)

        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")

        bm.to_mesh(mesh)
        bm.free()

        bytestring = b"mesh\x07\x00\x01\x00"

        colour_layer = None
        if len(mesh.vertex_colors) != 0:
            colour_layer = mesh.vertex_colors[0].data

        mesh.calc_loop_triangles()

        vertices = [None] * len(mesh.vertices)
        for triangle in mesh.loop_triangles:
            for loop_index in triangle.loops:
                loop = mesh.loops[loop_index]
                vertex_index = loop.vertex_index

                vertex = mesh.vertices[vertex_index]

                position = vertex.co

                colour = 255, 255, 255, 255
                if colour_layer is not None:
                    colour = *map(lambda a: int(a * 255), colour_layer[loop_index].color),

                vertices[vertex_index] = [position, None, colour]

        mesh.calc_normals_split()

        for triangle in mesh.loop_triangles:
            for loop_index in triangle.loops:
                loop = mesh.loops[loop_index]
                vertex_index = loop.vertex_index

                position, _, colour = *vertices[vertex_index],
                position[1], position[2] = position[2], position[1]

                normal = loop.normal
                normal[1], normal[2] = normal[2], normal[1]

                vertices[vertex_index] = [position, normal, colour]

        assert len(vertices) <= 2 ** 16

        bytestring = ExportStormworksMesh._put(bytestring, "H", len(vertices))
        bytestring = ExportStormworksMesh._write(bytestring, b"\x13\x00\x00\x00")

        min_pos = [0, 0, 0]
        max_pos = [0, 0, 0]

        for vertex in vertices:
            position, normal, colour = vertex

            for i in range(3):
                min_pos[i] = min(min_pos[i], position[i])
                max_pos[i] = max(max_pos[i], position[i])

            bytestring = ExportStormworksMesh._put(bytestring, "fff", *position)

            bytestring = ExportStormworksMesh._put(bytestring, "BBBB", *colour)
            bytestring = ExportStormworksMesh._put(bytestring, "fff", *normal)

        assert len(mesh.loop_triangles) * 3 <= 2 ** 32

        bytestring = ExportStormworksMesh._put(bytestring, "I", len(mesh.loop_triangles) * 3)

        for triangle in mesh.loop_triangles:
            for loop_index in triangle.loops:
                vertex_index = mesh.loops[loop_index].vertex_index

                bytestring = ExportStormworksMesh._put(bytestring, "H", vertex_index)

        for i in range(3):
            if min_pos[i] == 0:
                min_pos[i] -= 0.125

            if max_pos[i] == 0:
                max_pos[i] += 0.125

        bytestring = ExportStormworksMesh._put(bytestring, "H", 1)

        bytestring = ExportStormworksMesh._put(bytestring, "II", 0, len(mesh.loop_triangles) * 3)

        bytestring = ExportStormworksMesh._write(bytestring, b"\x00\x00")

        bytestring = ExportStormworksMesh._put(bytestring, "H", 0)

        bytestring = ExportStormworksMesh._put(bytestring, "fff", *min_pos)
        bytestring = ExportStormworksMesh._put(bytestring, "fff", *max_pos)

        # No idea what these bytes do so yeah
        bytestring = ExportStormworksMesh._write(bytestring,
                                                 b"\x00\x00\x03\x00\x49\x44\x30\x00\x00\x80\x3F\x00\x00\x80\x3F\x00\x00"
                                                 b"\x80\x3F")

        bytestring = ExportStormworksMesh._write(bytestring, b"\x00\x00")

        with open(filepath, "wb") as output:
            output.write(bytestring)

    @staticmethod
    def export_mesh(context, filepath: str) -> None:
        print(f"Exporting to {filepath}")
        ExportStormworksMesh.write_mesh(filepath)
        print(f"Finished Exporting")

    def execute(self, context) -> Set[str]:
        ExportStormworksMesh.export_mesh(context, self.filepath)
        return {"FINISHED"}
