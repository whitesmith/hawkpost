from django.utils import timezone
from datetime import datetime
from functools import wraps
from shutil import rmtree
import gnupg
import tempfile


def with_gpg_obj(func):
    @wraps(func)
    def inner(key):
        # create temp gpg keyring
        temp_dir = tempfile.mkdtemp()
        gpg_obj = gnupg.GPG(homedir=temp_dir,
                            keyring="pub.gpg",
                            secring="sec.gpg")
        ret = func(key, gpg_obj)
        # remove the keyring
        rmtree(temp_dir)
        return ret
    return inner


@with_gpg_obj
def key_state(key, gpg):
    results = gpg.import_keys(key).results
    keys = gpg.list_keys()
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
