import xml.etree.ElementTree as ET

from .transformation import Transformation


class Mesh:
    meshId: str
    filename: str
    seasonalFlags: str
    transformation: Transformation

    def __init__(self, xml: ET.Element) -> None:
        attributes = xml.attrib

        self.meshId = attributes["id"]
        self.filename = attributes["file_name"].replace("meshes/", "")
        self.seasonalFlags = attributes["seasonal_flags"]

        transformation = xml.find("transform")

        self.transformation = Transformation(transformation)
