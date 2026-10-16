from dataclasses import dataclass, field

from .position import Position


@dataclass(slots=True)
class Signer:
    first_name: str
    last_name: str
    email: str
    phone: str
    priority: int = 1
    positions: list[Position] = field(default_factory=list)

    def __post_init__(self):
        if not self.first_name.strip():
            raise ValueError("Le prénom est obligatoire.")

        if not self.last_name.strip():
            raise ValueError("Le nom est obligatoire.")

        if "@" not in self.email:
            raise ValueError("L'adresse e-mail semble invalide.")

        if self.priority < 1:
            raise ValueError("La priorité doit être supérieure ou égale à 1.")