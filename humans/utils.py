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
    if not key:
        return None, "invalid", -1
    results = gpg.import_keys(key).results
    # Key data is present in the last element of the list
    if not results or not results[-1]["fingerprint"]:
        return None, "invalid", -1

    key_fingerprint = results[-1]["fingerprint"]

    # Since the keyring is exclusive for this import
    # only the imported key exists in it.
    key = gpg.list_keys()[0]
    exp_timestamp = int(key["expires"]) if key["expires"] else 0
    expires = datetime.fromtimestamp(exp_timestamp, timezone.utc)
    to_expire = expires - timezone.now()
    days_to_expire = to_expire.days

    if key["trust"] == "r":
        state = "revoked"
    elif exp_timestamp and expires < timezone.now():
        state = "expired"
    else:
        state = "valid"

    return key_fingerprint, state, days_to_expire
