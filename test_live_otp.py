import os

from dkbsign import DKBSign


token = os.environ.get("DKBSIGN_API_TOKEN")

if not token:
    raise SystemExit("DKBSIGN_API_TOKEN variable not found.")

phone = os.environ.get("DKBSIGN_WHATSAPP_PHONE")
whatsapp_message = os.environ.get(
    "DKBSIGN_WHATSAPP_MESSAGE",
    "Your verification code is 000000",
)

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

if phone:
    try:
        result = client.send_whatsapp_otp(
            phone_number=phone,
            message=whatsapp_message,
        )
        print("Statut WhatsApp :", result["status_code"])
        print("Réponse :", result["body"])
    except Exception as exc:
        print("Échec WhatsApp :", exc)
else:
    print(
        "WhatsApp ignoré : définissez DKBSIGN_WHATSAPP_PHONE "
        "pour tester send_whatsapp_otp()."
    )
