from dataclasses import dataclass


@dataclass
class Position:
    x: float
    y: float
    width: float
    height: float
    page: float | None = None
    signature_type: str | None = None
    document_index: int = 0