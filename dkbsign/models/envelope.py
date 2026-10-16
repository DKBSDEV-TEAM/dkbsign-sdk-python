from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EnvelopeResult:
    status_code: int
    body: dict[str, Any]

    @property
    def batch_id(self):
        return self.body.get("batch_id")

    @property
    def signers(self):
        return self.body.get("signers", [])