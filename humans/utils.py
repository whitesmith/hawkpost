from django.conf import settings
from django.utils import timezone
from datetime import datetime


def key_state(key):
    results = settings.GPG_OBJ.import_keys(key).results
    keys = settings.GPG_OBJ.list_keys()
    if not results or not results[0]["fingerprint"]:
        return None, "invalid"
    else:
        state = "valid"
        result = results[0]
    for key in keys:
        if key["fingerprint"] == result["fingerprint"]:
            exp_timestamp = int(key["expires"]) if key["expires"] else 0
            expires = datetime.fromtimestamp(exp_timestamp, timezone.utc)
            if key["trust"] == "r":
                state = "revoked"
            elif exp_timestamp and expires < timezone.now():
                state = "expired"
            break
    return result["fingerprint"], state
