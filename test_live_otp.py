import os

from dkbsign import DKBSign


token = os.environ.get("DKBSIGN_API_TOKEN")

if not token:
    raise SystemExit("Variable DKBSIGN_API_TOKEN absente.")

client = DKBSign(
    "https://api.dkbsigns.com",
    token,
)

try:
    result = client.send_otp()
    print("Statut HTTP :", result["status_code"])
    print("Réponse API :", result["body"])
except Exception as exc:
    print("Échec du test :", exc)