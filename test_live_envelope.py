import os
from dkbsign.client import DKBSign

client = DKBSign(
    base_url="https://api.dkbsigns.com",
    api_token=os.environ["DKBSIGN_API_TOKEN"],
)

response = (
    client
    .set_documents([
        "document_test.pdf",
        "annexe_test.pdf",
    ])
    .set_attachments(
        0,
        ["piece_jointe.pdf"],
    )
    .set_envelope_title("Contrat de test")
    .set_envelope_description(
        "Merci de signer les documents."
    )
    .set_signature_order("ordered")
    .set_signers([
        {
            "first_name": "Awa",
            "last_name": "Kone",
            "email": "amoin.yao@dkbsolutions.com",
            "phone": "+2250173946589",
            "priority": 1,
            "positions": {
                "0": [
                    {
                        "page": 0,
                        "x": 120,
                        "y": 200,
                        "width": 200,
                        "height": 70,
                        "field_type": "signature",
                    }
                ],
                "1": [
                    {
                        "page": 0,
                        "x": 120,
                        "y": 200,
                        "width": 200,
                        "height": 70,
                        "field_type": "signature",
                    }
                ],
            },
        }
    ])
    .envelopes()
)

print("Code HTTP :", response["status_code"])
print("Réponse :", response["body"])
