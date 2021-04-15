import xml.etree.ElementTree as ET

from .transformation import Transformation


class Mesh:
    mesh_id: str
    filename: str
    seasonal_flags: str
    transformation: Transformation

    def __init__(self, xml: ET.Element) -> None:
        attributes = xml.attrib

        self.mesh_id = attributes["id"]
        self.filename = attributes["file_name"].replace("meshes/", "")
        self.seasonal_flags = attributes["seasonal_flags"]

        transformation = xml.find("transform")

        self.transformation = Transformation(transformation)
