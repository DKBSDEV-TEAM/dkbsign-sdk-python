from pathlib import Path

import requests

from .enums import SignatureLevel, SignatureType
from .signature import Signature
from .exceptions import DKBSignAPIError


class DKBSign:

    def __init__(self, base_url: str, api_token: str):

        self.base_url = base_url.rstrip("/")
        self.api_token = api_token

        self.document = None
        self.signature_image_file = None
        self.signature_level_value = SignatureLevel.SIMPLE.value

        self.signatures = {}

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        } 
    def file(self, file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document introuvable : {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Le document doit être un fichier PDF."
            )

        self.document = path

        return self     
    def signature_image(self, image_path: str):

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image de signature introuvable : {image_path}"
            )

        self.signature_image_file = path

        return self 
    def signature_level(self, level: str):

        self.signature_level_value = level

        return self 
    def signature(self, page: int, signatures: list[Signature]):

        self.signatures[page] = signatures

        return self