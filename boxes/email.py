from django.conf import settings

from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_noop, encode_7or8bit
from email.mime.application import MIMEApplication
from email.utils import formatdate

from django.core.mail import EmailMessage
from django.core.mail import SafeMIMEMultipart
from django.core.mail.message import make_msgid
from django.utils.encoding import force_text

from gnupg import GPG

# Create a message from an encrypted body and sign it.
# It assumes the following format:
#
#  multipart/signed
#  +--multipart/encrypted
#  |  +--application/pgp-encrypted
#  |  +--application/octet-stream
#  +--application/pgp-signature
#
# References:
# RFC 1847: Security Multiparts for MIME: Multipart/Signed and Multipart/Encrypted
# https://tools.ietf.org/html/rfc1847
#
# RFC 3156: MIME Security with OpenPGP
# https://tools.ietf.org/html/rfc3156
class GPGSignedEncryptedMessage(EmailMessage):
    DIGEST_ALGO='SHA512'

    def _set_headers(self, msg):
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = self.extra_headers.get('To', ', '.join(map(force_text, self.to)))
        if self.cc:
            msg['Cc'] = ', '.join(map(force_text, self.cc))
        if self.reply_to:
            msg['Reply-To'] = self.extra_headers.get('Reply-To', ', '.join(map(force_text, self.reply_to)))

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            # Use cached DNS_NAME for performance
            msg['Message-ID'] = make_msgid()
        for name, value in self.extra_headers.items():
            if name.lower() in ('from', 'to'):  # From and To are already handled
                continue
            msg[name] = value

    def _create_multipart_encrypted(self):
        multipart_encrypted = MIMEMultipart(
                _subtype="encrypted",
                protocol="application/pgp-encrypted")
        del multipart_encrypted['MIME-Version']

        # Control info
        control_info_part = MIMEApplication(
            'Version: 1\r\n',
            _subtype="pgp-encrypted",
            _encoder=encode_noop
          )
        del control_info_part['MIME-Version']

        # Stream (the encrypted data)
        stream_part = MIMEApplication(
            self.body,
            _subtype='octet-stream',
            _encoder=encode_7or8bit)
        del stream_part['MIME-Version']

        ## Attach both to the multipart
        multipart_encrypted.attach(control_info_part)
        multipart_encrypted.attach(stream_part)

        return multipart_encrypted

    def _sign(self, data, digest_algo):
        gpg = GPG(homedir=settings.GPG_SIGN_DIR)
        if not gpg.list_keys():
            # Import key if no private key key in keyring
            with open(settings.GPG_SIGN_KEY, 'r') as f:
                key = f.read()
            gpg.import_keys(key)

        signature = gpg.sign(data,
           passphrase=settings.GPG_SIGN_KEY_PASSPHRASE,
           clearsign=False,
           detach=True,
           digest_algo=digest_algo)

        return str(signature)

    def _create_signature_part(self, signature):
        signature_part = Message()
        signature_part['Content-Type'] = 'application/pgp-signature; name="signature.asc"'
        signature_part['Content-Description'] = 'OpenPGP digital signature'
        signature_part.set_payload(signature)

        return signature_part

    def message(self):
        # Construct multipart/signed
        multipart_signed = SafeMIMEMultipart(
                _subtype="signed",
                micalg="pgp-{0}".format(self.DIGEST_ALGO.lower()),
                protocol="application/pgp-signature")

        self._set_headers(multipart_signed)

        # Construct multipart/encrypted
        multipart_encrypted = self._create_multipart_encrypted()

        # Sign the encrypted multipart
        multipart_encrypted_text = multipart_encrypted.as_string().replace('\n', '\r\n')
        signature = self._sign(multipart_encrypted_text, self.DIGEST_ALGO)

        # Construct the signature part from signature
        signature_part = self._create_signature_part(signature)

        ## Attach both the multipart/encrypted and the signature
        multipart_signed.attach(multipart_encrypted)
        multipart_signed.attach(signature_part)

        return multipart_signed
