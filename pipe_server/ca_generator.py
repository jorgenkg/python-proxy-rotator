from tempfile import gettempdir
from os import path, listdir
from OpenSSL.crypto import (X509Extension, X509, dump_privatekey, dump_certificate, load_certificate, load_privatekey,
                            PKey, TYPE_RSA, X509Req)
from OpenSSL.SSL import FILETYPE_PEM

class CertificateAuthority(object):

    def __init__(self, ssl_certificate='ca.pem', cache_dir=gettempdir()):
        self.ssl_certificate = ssl_certificate
        self.cache_dir = cache_dir
        self._serial = self._get_serial()
        if not path.exists(ssl_certificate):
            self._generate_ca()
        else:
            self._read_ca(ssl_certificate)

    def _get_serial(self):
        s = 1
        for c in filter(lambda x: x.startswith('.pymp_'), listdir(self.cache_dir)):
            c = load_certificate(FILETYPE_PEM, open(path.sep.join([self.cache_dir, c])).read())
            sc = c.get_serial_number()
            if sc > s:
                s = sc
            del c
        return s

    def _generate_ca(self):
        # Generate key
        self.key = PKey()
        self.key.generate_key(TYPE_RSA, 2048)

        # Generate certificate
        self.cert = X509()
        self.cert.set_version(3)
        self.cert.set_serial_number(1)
        self.cert.get_subject().CN = 'Python proxychain server'
        self.cert.gmtime_adj_notBefore(0)
        self.cert.gmtime_adj_notAfter(315360000)
        self.cert.set_issuer(self.cert.get_subject())
        self.cert.set_pubkey(self.key)
        self.cert.add_extensions([
            X509Extension("basicConstraints", True, "CA:TRUE, pathlen:0"),
            X509Extension("keyUsage", True, "keyCertSign, cRLSign"),
            X509Extension("subjectKeyIdentifier", False, "hash", subject=self.cert),
            ])
        self.cert.sign(self.key, "sha1")

        with open(self.ssl_certificate, 'wb+') as f:
            f.write(dump_privatekey(FILETYPE_PEM, self.key))
            f.write(dump_certificate(FILETYPE_PEM, self.cert))

    def _read_ca(self, file):
        self.cert = load_certificate(FILETYPE_PEM, open(file).read())
        self.key = load_privatekey(FILETYPE_PEM, open(file).read())

    def __getitem__(self, cn):
        cnp = path.sep.join([self.cache_dir, '.pymp_%s.pem' % cn])
        if not path.exists(cnp):
            # create certificate
            key = PKey()
            key.generate_key(TYPE_RSA, 2048)

            # Generate CSR
            req = X509Req()
            req.get_subject().CN = cn
            req.set_pubkey(key)
            req.sign(key, 'sha1')

            # Sign CSR
            cert = X509()
            cert.set_subject(req.get_subject())
            cert.set_serial_number(self.serial)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(31536000)
            cert.set_issuer(self.cert.get_subject())
            cert.set_pubkey(req.get_pubkey())
            cert.sign(self.key, 'sha1')

            with open(cnp, 'wb+') as f:
                f.write(dump_privatekey(FILETYPE_PEM, key))
                f.write(dump_certificate(FILETYPE_PEM, cert))

        return cnp

    @property
    def serial(self):
        self._serial += 1
        return self._serial