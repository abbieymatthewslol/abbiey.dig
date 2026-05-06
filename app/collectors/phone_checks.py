from typing import Any

import phonenumbers
from phonenumbers import NumberParseException


def run(phone: str, default_region: str = "US") -> dict[str, Any]:
    raw = phone.strip()
    out: dict[str, Any] = {"input": phone}
    if not raw:
        out["valid"] = False
        out["error"] = "Empty phone number"
        return out

    try:
        pn = phonenumbers.parse(raw, default_region)
    except NumberParseException as e:
        out["valid"] = False
        out["error"] = str(e)
        return out

    out["valid"] = phonenumbers.is_valid_number(pn)
    out["possible"] = phonenumbers.is_possible_number(pn)
    out["region_code"] = phonenumbers.region_code_for_number(pn)
    out["e164"] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
    out["international"] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    out["national"] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
    return out

