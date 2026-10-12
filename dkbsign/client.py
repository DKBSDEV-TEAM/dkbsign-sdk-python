import json
from pathlib import Path

import requests

from .enums import SignatureLevel
from .exceptions import DKBSignAPIError
from .signature import Signature


class DKBSign:
       def __init__(self, base_url: str, api_token: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.session = requests.Session() 
        self.document = None
        self.signature_image_file = None
        self.signature_level_value = SignatureLevel.SIMPLE.value
        self.pages = []

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        } 

        
       @staticmethod
       def _image_mime_type():
        return "image/png"


       def send_otp(self):
        return self._post_json("/api/v4/sign/otp") 
    
       def _post_json(self, path: str):
        try:
            response = self.session.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=[],
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise DKBSignAPIError(f"Erreur réseau : {exc}") from exc

        return self._handle_response(response)  

       @staticmethod
       def _handle_response(response):
        try:
            body = response.json()
        except ValueError:
            body = {"message": response.text}

        result = {
            "status_code": response.status_code,
            "body": body,
        }

        if not response.ok:
            raise DKBSignAPIError(
                f"HTTP {response.status_code}: {body}"
            )

        return result



       def set_file(self, file_path: str):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF introuvable : {file_path}")
        self.document = str(path.resolve())
        return self

       def set_signature_image(self, image_path: str):
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image introuvable : {image_path}")
        self.signature_image_file = str(path.resolve())
        return self

       def set_signature_level(self, level):
        if isinstance(level, SignatureLevel):
            level = level.value
        self.signature_level_value = str(level)
        return self

       def add_signature(self, page: int, signatures: list[Signature]):
        if page < 0:
            raise ValueError("La page ne peut pas être négative.")
        if not signatures:
            raise ValueError("Il faut au moins une signature.")

        self.pages.append({
            "page": page,
            "signatures": [
                {
                    "x": item.position.x,
                    "y": item.position.y,
                    "width": item.position.width,
                    "height": item.position.height,
                    "type": item.type,
                }
                for item in signatures
            ],
        })
        return self

       def self_sign(self, otp_code: str | int):
        if not self.document:
            raise ValueError("Appelle set_file() avant self_sign().")
        if not self.signature_image_file:
            raise ValueError(
                "Appelle set_signature_image() avant self_sign()."
            )
        if not self.pages:
            raise ValueError("Ajoute une signature avant self_sign().")

        params = {
            "pages": self.pages,
            "signature_level": self.signature_level_value,
            "otp_code": otp_code,
        }

        try:
            with open(self.document, "rb") as pdf, open(
                self.signature_image_file, "rb"
            ) as image:
                response = self.session.post(
                    f"{self.base_url}/api/v4/sign",
                    headers=self.headers,
                    data={"params": json.dumps(params)},
                    files={
                        "file": (
                            Path(self.document).name,
                            pdf,
                            "application/pdf",
                        ),
                        "signature_image": (
                            Path(self.signature_image_file).name,
                            image,
                            self._image_mime_type(),
                        ),
                    },
                    timeout=self.timeout,
                )
        except requests.RequestException as exc:
            raise DKBSignAPIError(f"Erreur réseau : {exc}") from exc

        return self._handle_response(response)

