from enum import Enum


class SignatureLevel(Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    QUALIFIED = "qualified"


class SignatureType(Enum):
    SIGNATURE = "signature"
    INITIALS = "initials"
    SEAL = "seal"
    QRCODE = "qrcode"
    DATE = "date"
    TEXT = "text"
    APPROVAL = "approval"