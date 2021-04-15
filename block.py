import xml.etree.ElementTree as ET
from typing import List

from .helpers import remove_prefix
from .surface import Surface


class Block:
    surfaces: List[Surface]
    meshname: str
    extra_meshes: List[str] = []

    def __init__(self, xml: ET.Element) -> None:
        attributes = xml.attrib
        self.meshname = remove_prefix(attributes["mesh_data_name"], "meshes/")

        for i in range(2):
            try:
                self.extra_meshes.append(remove_prefix(attributes[f"mesh_{i}_name"], "meshes/"))
            except IndexError:
                pass

        self.surfaces = []
        for surface in xml.find("surfaces"):
            self.surfaces.append(Surface(surface))
