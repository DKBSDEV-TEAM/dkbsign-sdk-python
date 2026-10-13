import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from dkbsign import DKBSign, Position, Signature, SignatureLevel
from dkbsign.exceptions import DKBSignAPIError


@pytest.fixture
def client():
    return DKBSign("https://api.example.com", "test-token", timeout=5)


def _mock_response(status_code=200, json_body=None, text="", ok=None):
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.text = text
    if ok is None:
        ok = 200 <= status_code < 300
    response.ok = ok
    if json_body is not None:
        response.json.return_value = json_body
    else:
        response.json.side_effect = ValueError("not json")
    return response


def test_handle_response_success():
    response = _mock_response(200, {"ok": True})
    result = DKBSign._handle_response(response)
    assert result == {"status_code": 200, "body": {"ok": True}}


def test_handle_response_non_json_success():
    response = _mock_response(200, json_body=None, text="plain")
    result = DKBSign._handle_response(response)
    assert result["body"] == {"message": "plain"}


def test_handle_response_raises_on_error():
    response = _mock_response(400, {"error": "bad"}, ok=False)
    with pytest.raises(DKBSignAPIError, match="HTTP 400"):
        DKBSign._handle_response(response)


def test_send_otp_posts_empty_json_list(client):
    response = _mock_response(200, {"sent": True})
    client.session.post = MagicMock(return_value=response)

    result = client.send_otp()

    client.session.post.assert_called_once_with(
        "https://api.example.com/api/v4/sign/otp",
        headers=client.headers,
        json=[],
        timeout=5,
    )
    assert result["body"] == {"sent": True}


def test_send_whatsapp_otp_validates_phone(client):
    with pytest.raises(ValueError, match="\\+"):
        client.send_whatsapp_otp("22501020304", "hello")


def test_send_whatsapp_otp_validates_message_length(client):
    with pytest.raises(ValueError, match="255"):
        client.send_whatsapp_otp("+33123456789", "x" * 256)


def test_send_whatsapp_otp_accepts_202(client):
    response = _mock_response(202, {"queued": True})
    client.session.post = MagicMock(return_value=response)

    result = client.send_whatsapp_otp("+33123456789", "Your code is 123")

    assert result["status_code"] == 202
    payload = client.session.post.call_args.kwargs["json"]
    assert payload["channel"] == "whatsapp"


def test_set_file_missing_raises(client, tmp_path):
    missing = tmp_path / "nope.pdf"
    with pytest.raises(FileNotFoundError):
        client.set_file(str(missing))


def test_add_signature_validates_page_and_list(client):
    sig = Signature(position=Position(0, 0, 10, 10))
    with pytest.raises(ValueError, match="négative"):
        client.add_signature(-1, [sig])
    with pytest.raises(ValueError, match="au moins une"):
        client.add_signature(0, [])


def test_add_signature_builds_pages(client):
    sig = Signature(position=Position(1, 2, 3, 4), type="signature")
    client.add_signature(0, [sig])
    assert client.pages == [
        {
            "page": 0,
            "signatures": [
                {"x": 1, "y": 2, "width": 3, "height": 4, "type": "signature"}
            ],
        }
    ]


def test_self_sign_requires_document_image_and_pages(client):
    with pytest.raises(ValueError, match="set_file"):
        client.self_sign("000000")
    client.document = "/tmp/doc.pdf"
    with pytest.raises(ValueError, match="set_signature_image"):
        client.self_sign("000000")
    client.signature_image_file = "/tmp/img.png"
    with pytest.raises(ValueError, match="Ajoute une signature"):
        client.self_sign("000000")


def test_self_sign_multipart_payload(client, tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    img = tmp_path / "sig.jpg"
    img.write_bytes(b"\xff\xd8\xff")

    client.set_file(str(pdf))
    client.set_signature_image(str(img))
    client.set_signature_level(SignatureLevel.ADVANCED)
    client.add_signature(1, [Signature(position=Position(10, 20, 30, 40))])

    api_response = _mock_response(200, {"signed": True})
    client.session.post = MagicMock(return_value=api_response)

    result = client.self_sign(987654)

    assert result["body"]["signed"] is True
    call_kwargs = client.session.post.call_args.kwargs
    assert call_kwargs["data"]["params"]
    params = json.loads(call_kwargs["data"]["params"])
    assert params["signature_level"] == "advanced"
    assert params["otp_code"] == 987654
    assert params["pages"][0]["page"] == 1

    files = call_kwargs["files"]
    assert files["signature_image"][2] == "image/jpeg"


def test_image_mime_type_from_extension():
    assert DKBSign._image_mime_type("a.png") == "image/png"
    assert DKBSign._image_mime_type(Path("b.JPEG")) == "image/jpeg"
    assert DKBSign._image_mime_type("unknown.bin") == "image/png"


def test_reset_clears_signing_state(client, tmp_path):
    pdf = tmp_path / "d.pdf"
    pdf.write_bytes(b"x")
    client.set_file(str(pdf))
    client.set_signature_image(str(pdf))
    client.add_signature(0, [Signature(position=Position(0, 0, 1, 1))])

    client.reset()

    assert client.document is None
    assert client.signature_image_file is None
    assert client.pages == []
    assert client.signature_level_value == SignatureLevel.SIMPLE.value
