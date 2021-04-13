import xml.etree.ElementTree as ET
from typing import List

from .mesh import Mesh


class Tile:
    meshes: List[Mesh]

    def __init__(self, xml: ET.Element) -> None:
        self.meshes = []
        for mesh in xml.find("meshes"):
            self.meshes.append(Mesh(mesh))
