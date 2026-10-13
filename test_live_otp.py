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


try:
    result = client.send_whatsapp_otp(
        phone_number="+2250173946589",
        message="Your code is 00990"
    )
    print("Statut WhatsApp :", result["status_code"])
    print("Réponse :", result["body"])

except Exception as exc:
    print("Échec :", exc)
