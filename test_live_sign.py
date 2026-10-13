
import os
from getpass import getpass
from dkbsign import DKBSign, Signature, Position, SignatureLevel

token = os.environ.get("DKBSIGN_API_TOKEN")

if not token:
    raise SystemExit("Token API absent. Configure-le dans PowerShell.")

pdf_path = "Document_test_.pdf"
image_path = "signature.png"

if not os.path.isfile(pdf_path):
    raise SystemExit(f"PDF introuvable : {pdf_path}")

if not os.path.isfile(image_path):
    raise SystemExit(f"Image introuvable : {image_path}")

otp_code = getpass("Entre le code OTP reçu par e-mail : ")

client = DKBSign(
    "https://api.dkbsigns.com",
    token,
)

try:
    response = (
        client
        .set_file(pdf_path)
        .set_signature_image(image_path)
        .set_signature_level(SignatureLevel.SIMPLE)
        .add_signature(
            0,
            [
                Signature(
                    position=Position(
                        x=120,
                        y=200,
                        width=200,
                        height=70,
                    ),
                    type="signature",
                )
            ],
        )
        .self_sign(otp_code)
    )

    print("Statut HTTP :", response["status_code"])
    print("Réponse API :", response["body"])

except Exception as exc:
    print("Échec de la signature :", exc)
