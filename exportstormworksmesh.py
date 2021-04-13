import struct
from typing import Set

import bmesh
import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper


class ExportStormworksMesh(Operator, ExportHelper):
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
        packedBytes = struct.pack(structure, *values)

        return bytestring + packedBytes

    @staticmethod
    def _write(bytestring: bytes, bytestowrite: bytes) -> bytes:
        return bytestring + bytestowrite

    @staticmethod
    def write_mesh(filepath: str) -> None:
        obj = bpy.context.object

        assert obj and obj.type == "MESH"

        mesh = obj.data

        bm = bmesh.new()
        bm.from_mesh(mesh)

        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")

        bytestring = b"mesh"

        bytestring = ExportStormworksMesh._write(bytestring, b"\x07\x00\x01\x00")
        bytestring = ExportStormworksMesh._put(bytestring, "H", len(bm.verts))
        bytestring = ExportStormworksMesh._write(bytestring, b"\x13\x00\x00\x00")

        colourMap = []
        if len(mesh.vertex_colors) != 0:
            colourMap = mesh.vertex_colors[0]

        bm.verts.ensure_lookup_table()

        for i in range(len(bm.verts)):
            vertex = bm.verts[i]

            colour = 255, 255, 255, 255
            if i < len(colourMap):
                colour = *map(lambda a: a * 255, colourMap[i]),

            bytestring = ExportStormworksMesh._put(bytestring, "fff", vertex.co.x, vertex.co.y, vertex.co.z)
            bytestring = ExportStormworksMesh._put(bytestring, "BBBB", *colour)
            bytestring = ExportStormworksMesh._put(bytestring, "fff", vertex.normal.x, vertex.normal.y,
                                                   vertex.normal.z)

        bytestring = ExportStormworksMesh._put(bytestring, "I", len(bm.faces) * 3)

        for triangle in bm.faces:
            bytestring = ExportStormworksMesh._put(bytestring, "HHH", *map(lambda a: a.index, triangle.verts))

        bytestring = ExportStormworksMesh._put(bytestring, "I", 0)

        bytestring = ExportStormworksMesh._write(bytestring, b"\x00\x00")

        with open(filepath, "wb") as output:
            output.write(bytestring)

    @staticmethod
    def export_mesh(context, filepath: str) -> None:
        print(f"Exporting to {filepath}")
        ExportStormworksMesh.writeMesh(filepath)
        print(f"Finished Exporting")

    def execute(self, context) -> Set[str]:
        ExportStormworksMesh.export_mesh(context, self.filepath)
        return {"FINISHED"}
