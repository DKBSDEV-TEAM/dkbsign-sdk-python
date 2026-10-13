from dataclasses import dataclass

from .enums import SignatureType
from .position import Position


@dataclass
class Signature:
    position: Position
    type: str = SignatureType.SIGNATURE.value