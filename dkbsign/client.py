
import json
from pathlib import Path

import requests
from contextlib import ExitStack
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

                # Configuration de la création d'enveloppes
        self.documents = []
        self.attachments = {}
        self.envelope_title = ""
        self.envelope_description = ""
        self.signature_order = "ordered"
        self.signers = []

    @staticmethod
    def _image_mime_type(path: str | Path) -> str:
        suffix = Path(path).suffix.lower()
        return {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(suffix, "image/png")

    def reset(self):
        """Réinitialise document, image, emplacements et niveau de signature."""
        self.document = None
        self.signature_image_file = None
        self.signature_level_value = SignatureLevel.SIMPLE.value
        self.pages = []
        return self

    def send_otp(self):
        return self._post_json("/api/v4/sign/otp")

    def send_whatsapp_otp(
        self, phone_number: str, message: str
    ):
        if not phone_number.startswith("+"):
            raise ValueError(
                "Le numéro doit commencer par + et inclure "
                "l'indicatif du pays."
            )

        if len(message) > 255:
            raise ValueError(
                "Le message ne doit pas dépasser 255 caractères."
            )

        try:
            response = self.session.post(
                f"{self.base_url}/api/notifications/sms",
                headers=self.headers,
                json={
                    "channel": "whatsapp",
                    "phone_number": phone_number,
                    "message": message,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise DKBSignAPIError(
                f"Erreur lors de l'envoi WhatsApp : {exc}"
            ) from exc

        if response.status_code != 202:
            raise DKBSignAPIError(
                f"Échec de la notification WhatsApp : "
                f"HTTP {response.status_code} - {response.text}"
            )

        try:
            body = response.json()
        except ValueError:
            body = {"message": response.text}

        return {
            "status_code": response.status_code,
            "body": body,
        }

    def _post_json(self, path: str):
        try:
            response = self.session.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=[],
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise DKBSignAPIError(
                f"Erreur réseau : {exc}"
            ) from exc

        return self._handle_response(response) 

    
    def envelopes(self):
        """Crée une enveloppe avec plusieurs documents et signataires."""
        if not self.documents:
            raise ValueError(
                "Appelle set_documents() avant envelopes()."
            )

        if not self.envelope_title:
            raise ValueError(
                "Appelle set_envelope_title() avant envelopes()."
            )

        if not self.signers:
            raise ValueError(
                "Appelle set_signers() avant envelopes()."
            )

        payload = {
            "title": self.envelope_title,
            "message": self.envelope_description,
            "signing_order": self.signature_order,
            "signature_level": self.signature_level_value,
            "signers": self.signers,
        }

        files = []

        try:
            with ExitStack() as stack:
                # Documents principaux : documents[]
                for file_path in self.documents:
                    stream = stack.enter_context(
                        open(file_path, "rb")
                    )

                    files.append((
                        "documents[]",
                        (
                            Path(file_path).name,
                            stream,
                            "application/pdf",
                        ),
                    ))

                # Pièces jointes : attachments_{index}[]
                for document_index, paths in self.attachments.items():
                    for file_path in paths:
                        stream = stack.enter_context(
                            open(file_path, "rb")
                        )

                        files.append((
                            f"attachments_{document_index}[]",
                            (
                                Path(file_path).name,
                                stream,
                                "application/pdf"
                                if Path(file_path).suffix.lower() == ".pdf"
                                else "application/octet-stream",
                            ),
                        ))

                # Le payload est envoyé comme champ multipart.
                response = self.session.post(
                    f"{self.base_url}/api/v4/envelopes",
                    headers=self.headers,
                    data={"payload": json.dumps(payload)},
                    files=files,
                    timeout=self.timeout,
                )

        except requests.RequestException as exc:
            raise DKBSignAPIError(
                f"Erreur réseau lors de la création "
                f"de l'enveloppe : {exc}"
            ) from exc

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
            raise FileNotFoundError(
                f"PDF introuvable : {file_path}"
            )

        self.document = str(path.resolve())
        return self

    def set_signature_image(self, image_path: str):
        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Image introuvable : {image_path}"
            )

        self.signature_image_file = str(path.resolve())
        return self

    def set_signature_level(self, level):
        if isinstance(level, SignatureLevel):
            level = level.value

        self.signature_level_value = str(level)
        return self 


    
    def set_documents(self, paths: list[str]):
        """Définit les PDF qui composeront l'enveloppe."""
        if not paths:
            raise ValueError("Il faut au moins un document PDF.")

        documents = []

        for file_path in paths:
            path = Path(file_path)

            if not path.is_file():
                raise FileNotFoundError(
                    f"Document introuvable : {file_path}"
                )

            if path.suffix.lower() != ".pdf":
                raise ValueError(
                    f"Le document doit être un PDF : {file_path}"
                )

            documents.append(str(path.resolve()))

        self.documents = documents
        self.attachments = {}
        return self

    def set_attachments(
        self, document_index: int, paths: list[str]
    ):
        """Ajoute des pièces jointes à un document de l'enveloppe."""
        if not self.documents:
            raise ValueError(
                "Appelle set_documents() avant set_attachments()."
            )

        if not 0 <= document_index < len(self.documents):
            raise ValueError(
                "L'index du document est invalide."
            )

        attachments = []

        for file_path in paths:
            path = Path(file_path)

            if not path.is_file():
                raise FileNotFoundError(
                    f"Pièce jointe introuvable : {file_path}"
                )

            attachments.append(str(path.resolve()))

        self.attachments[document_index] = attachments
        return self

    def set_envelope_title(self, title: str):
        if not title or not title.strip():
            raise ValueError("Le titre est obligatoire.")

        self.envelope_title = title.strip()
        return self

    def set_envelope_description(self, description: str):
        self.envelope_description = description
        return self

    def set_signature_order(self, order: str):
        if order not in ("ordered", "any"):
            raise ValueError(
                "L'ordre doit être 'ordered' ou 'any'."
            )

        self.signature_order = order
        return self

    def set_signers(self, signers: list[dict]):
        """Enregistre les signataires au format API."""
        if not signers:
            raise ValueError(
                "Il faut au moins un signataire."
            )

        required = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "priority",
            "positions",
        )

        for index, signer in enumerate(signers):
            missing = [
                key for key in required if key not in signer
            ]

            if missing:
                raise ValueError(
                    f"Signataire {index + 1} : "
                    f"champs manquants : {', '.join(missing)}"
                )

            if not str(signer["phone"]).startswith("+"):
                raise ValueError(
                    f"Le téléphone du signataire {index + 1} "
                    "doit inclure l'indicatif international."
                )

        self.signers = signers
        return self


    def add_signature(self, page: int, signatures: list[Signature]):
        if page < 0:
            raise ValueError(
                "La page ne peut pas être négative."
            )

        if not signatures:
            raise ValueError(
                "Il faut au moins une signature."
            )

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
            raise ValueError(
                "Appelle set_file() avant self_sign()."
            )

        if not self.signature_image_file:
            raise ValueError(
                "Appelle set_signature_image() avant self_sign()."
            )

        if not self.pages:
            raise ValueError(
                "Ajoute une signature avant self_sign()."
            )

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
                            self._image_mime_type(
                                self.signature_image_file
                            ),
                        ),
                    },
                    timeout=self.timeout,
                )
        except requests.RequestException as exc:
            raise DKBSignAPIError(
                f"Erreur réseau : {exc}"
            ) from exc

        return self._handle_response(response)


