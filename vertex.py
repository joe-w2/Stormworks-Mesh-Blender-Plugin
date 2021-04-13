import math
from typing import List, Tuple

import numpy as np


def rotationMatrix(axis: np.array, theta: float) -> np.array:
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


class Vertex:
    x: float
    y: float
    z: float
    r: float
    g: float
    b: float
    a: float
    nx: float
    ny: float
    nz: float

    def __init__(self, x: float, y: float, z: float, r: float, g: float, b: float, a: float, nx: float, ny: float,
                 nz: float) -> None:
        self.z = z
        self.y = y
        self.x = x
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.nx = nx
        self.nz = nz
        self.ny = ny

    def transform(self, transformations: List[Tuple[Tuple[float, float, float], float]],
                  offset: Tuple[float, float, float]) -> None:
        for transformation in transformations:
            axis, angle = transformation

            vector = np.array([self.x, self.y, self.z])

            matrix = rotationMatrix(axis, angle)

            out = matrix.dot(vector)

            self.x, self.y, self.z = *out,

        self.x, self.y, self.z = self.x + offset[0] * 0.25, self.y + offset[1] * 0.25, self.z + offset[2] * 0.25
