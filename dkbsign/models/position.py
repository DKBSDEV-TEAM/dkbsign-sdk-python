from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int
    width: int
    height: int
    page: int = 0
    field_type: str = "signature"
    document_index: int = 0

    def __post_init__(self):
        if self.x < 0 or self.y < 0:
            raise ValueError("Les coordonnées doivent être positives.")

        if self.width <= 0 or self.height <= 0:
            raise ValueError("La largeur et la hauteur doivent être positives.")

        if self.page < 0 or self.document_index < 0:
            raise ValueError("La page et l'index du document doivent être positifs.")