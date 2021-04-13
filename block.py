import xml.etree.ElementTree as ET
from typing import List

from .helpers import remove_prefix
from .surface import Surface


class Block:
    surfaces: List[Surface]
    meshname: str

    def __init__(self, xml: ET.Element) -> None:
        attributes = xml.attrib
        self.meshname = remove_prefix(attributes["mesh_data_name"], "meshes/")

        if self.meshname == "component_robotic_pivot_b_no_trans.mesh":
            self.meshname = "assets_meshes_component_robotic_pivot_b_no_trans.mesh"

        self.surfaces = []
        for surface in xml.find("surfaces"):
            self.surfaces.append(Surface(surface))
