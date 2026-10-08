from dataclasses import dataclass


@dataclass
class Signature:
    position_x: int
    position_y: int
    width: int
    height: int
    type: str