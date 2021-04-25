from typing import Tuple


class Submesh:
    vertices: Tuple[int, int]
    shader: int

    def __init__(self, vertices: Tuple[int, int], shader: int) -> None:
        self.vertices = vertices
        self.shader = shader
