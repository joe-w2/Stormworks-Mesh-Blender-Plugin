import xml.etree.ElementTree as ET

from typing import Tuple


class Surface(object):
    orientation: int
    rotation: int
    shape: int
    transType: int
    position: Tuple[int, int, int]

    def __init__(self, xml: ET.Element) -> None:
        attributes = xml.attrib

        self.orientation = int(attributes["orientation"])
        self.rotation = int(attributes["rotation"])
        self.shape = int(attributes["shape"])
        self.transType = int(attributes["trans_type"])

        position = xml.find("position")
        attributes = position.attrib

        x, y, z = int(attributes["x"]), int(attributes["y"]), int(attributes["z"])
        self.position = x, y, z
