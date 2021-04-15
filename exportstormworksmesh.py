import math
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
        del bm

        bytestring = b"mesh"

        bytestring = ExportStormworksMesh._write(bytestring, b"\x07\x00\x01\x00")
        bytestring = ExportStormworksMesh._put(bytestring, "H", len(mesh.vertices))
        bytestring = ExportStormworksMesh._write(bytestring, b"\x13\x00\x00\x00")

        colour_layer = None
        if len(mesh.vertex_colors) != 0:
            colour_layer = mesh.vertex_colors[0].data

        mesh.calc_loop_triangles()

        vertices = [None] * len(mesh.vertices)
        for triangle in mesh.loop_triangles:
            for loop_index in triangle.loops:
                vertex_index = mesh.loops[loop_index].vertex_index

                vertex = mesh.vertices[vertex_index]

                position = vertex.co
                normal = vertex.normal

                colour = 255, 255, 255, 255
                if colour_layer is not None:
                    colour = *map(lambda a: math.floor(a * 255), colour_layer[loop_index].color),

                vertices[vertex_index] = (position, normal, colour)

        for vertex in vertices:
            position, normal, colour = *vertex,

            bytestring = ExportStormworksMesh._put(bytestring, "fff", *position)
            bytestring = ExportStormworksMesh._put(bytestring, "BBBB", *colour)
            bytestring = ExportStormworksMesh._put(bytestring, "fff", *normal)

        bytestring = ExportStormworksMesh._put(bytestring, "I", len(mesh.loop_triangles) * 3)

        for triangle in mesh.loop_triangles:
            for loop_index in triangle.loops:
                vertex_index = mesh.loops[loop_index].vertex_index

                bytestring = ExportStormworksMesh._put(bytestring, "H", vertex_index)

        bytestring = ExportStormworksMesh._put(bytestring, "I", 0)

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
