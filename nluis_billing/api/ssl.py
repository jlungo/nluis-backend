
from base64 import b64encode, b64decode
from OpenSSL import crypto


def ssl_verity(public_key, key_pass, data, signature):
    signature = str(signature)
    pfx = open(public_key, 'rb').read()
    cert = crypto.load_pkcs12(pfx, key_pass).get_certificate()

    if crypto.verify(cert, b64decode(signature), data, 'sha1WithRSAEncryption') is None:
        return True
    else:
        return False


def ssl_sign(data, private_key, key_pass):
    pfx = open(private_key, 'rb').read()
    pkey = crypto.load_pkcs12(pfx, key_pass).get_privatekey()

    return b64encode(crypto.sign(pkey, data, 'sha1WithRSAEncryption'))
