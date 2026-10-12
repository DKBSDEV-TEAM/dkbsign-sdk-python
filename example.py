from pathlib import Path

from dkbsign import (
    DKBSign,
    Signature,
    SignatureLevel,
    SignatureType,
)


client = DKBSign(
    base_url="https://api.dkbsigns.com",
    api_token="TOKEN_DE_TEST",
)

signature = Signature(
    position_x=120,
    position_y=200,
    width=200,
    height=70,
    type=SignatureType.SIGNATURE.value,
)

# Vérification de l'objet Signature
print("1. Objet Signature créé :")
print(signature)

# Vérification du chaînage et de la configuration
client.signature_level(SignatureLevel.SIMPLE)
client.signature(page=0, signatures=[signature])

print("\n2. Niveau de signature :")
print(client.signature_level_value)

print("\n3. Positions configurées :")
print(client._serialize_signatures())

print("\n4. URL OTP configurée :")
print(client._build_url(client.otp_path))

print("\n5. URL de signature configurée :")
print(client._build_url(client.sign_path))

# Vérification des fichiers sans effectuer d'appel réseau
if Path("document.pdf").is_file():
    client.file("document.pdf")
    print("\n6. Document PDF détecté.")
else:
    print("\n6. Aucun document.pdf : test de configuration uniquement.")

print("\nTest local terminé.")