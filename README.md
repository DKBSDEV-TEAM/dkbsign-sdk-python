# dkbsign-sdk-python

Client Python pour l’API [DKB Sign](https://api.dkbsigns.com) : envoi d’OTP, notification WhatsApp et signature PDF.

## Installation

```bash
pip install -e .
# ou avec les outils de dev
pip install -e ".[dev]"
```

Dépendance minimale : `requests` (voir aussi `requirements.txt`).

## Configuration

Définissez votre token API :

```powershell
$env:DKBSIGN_API_TOKEN = "votre_token"
```

## Exemple rapide

```python
from dkbsign import DKBSign, Position, Signature, SignatureLevel

client = DKBSign("https://api.dkbsigns.com", "YOUR_TOKEN")

client.send_otp()

response = (
    client
    .set_file("document.pdf")
    .set_signature_image("signature.png")
    .set_signature_level(SignatureLevel.SIMPLE)
    .add_signature(
        0,
        [
            Signature(
                position=Position(x=120, y=200, width=200, height=70),
            )
        ],
    )
    .self_sign("123456")
)
print(response["status_code"], response["body"])
```

Un exemple sans appel réseau est disponible dans `example.py`.

## Tests

```bash
pytest
```

Les scripts `test_live_otp.py` et `test_live_sign.py` appellent l’API réelle (token et fichiers requis).
