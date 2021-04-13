import xml.etree.ElementTree as ET

import numpy as np


class Transformation:
    matrix: np.array = None

    def __init__(self, xml: ET.Element) -> None:
        self.matrix = np.zeros((4, 4))

        for key, value in xml.attrib.items():
            row = int(key[1])
            col = int(key[2])
            value = float(value)

            self.matrix[row][col] = value
