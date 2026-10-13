"""Exemple local sans appel réseau (vérifie la configuration du client)."""

from pathlib import Path

from dkbsign import DKBSign, Position, Signature, SignatureLevel, SignatureType


client = DKBSign(
    base_url="https://api.dkbsigns.com",
    api_token="TOKEN_DE_TEST",
)

signature = Signature(
    position=Position(x=120, y=200, width=200, height=70),
    type=SignatureType.SIGNATURE.value,
)

print("1. Objet Signature créé :")
print(signature)

(
    client
    .set_signature_level(SignatureLevel.SIMPLE)
    .add_signature(page=0, signatures=[signature])
)

print("\n2. Niveau de signature :", client.signature_level_value)
print("\n3. Pages configurées :", client.pages)

pdf_candidates = ("document.pdf", "Document_test_.pdf")
for name in pdf_candidates:
    if Path(name).is_file():
        client.set_file(name)
        print(f"\n4. PDF détecté : {name}")
        break
else:
    print("\n4. Aucun PDF trouvé : configuration uniquement.")

if Path("signature.png").is_file():
    client.set_signature_image("signature.png")
    print("5. Image signature.png détectée.")
else:
    print("5. Aucune signature.png : configuration uniquement.")

print("\nExemple local terminé (aucun appel API).")
