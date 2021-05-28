#!/usr/bin/python
import os
import re
import sys

from OpenSSL.SSL import FILETYPE_PEM
from OpenSSL.crypto import (dump_certificate_request, PKey, TYPE_RSA, X509Req, X509Extension)

from config import CSR_CONFIG


def create_csr(domain, csr_file_path, key_file_path):
    private_key_path = re.sub(r".(pem|crt)$", ".key", key_file_path, flags=re.IGNORECASE)

    if not domain:
        print("Please set a domain!")
        sys.exit(1)

    if not csr_file_path:
        print("Please set the CSR file path!")
        sys.exit(1)

    if not key_file_path:
        print("Please set key file path!")
        sys.exit(1)

    # Create public/private key
    key = PKey()
    key.generate_key(TYPE_RSA, 2048)

    # Generate CSR
    req = X509Req()
    san = ("DNS:" + domain).encode('ascii')
    req.add_extensions([
        X509Extension(b"subjectAltName", False, san)
    ])

    req.get_subject().CN = domain
    req.get_subject().O = CSR_CONFIG['subject_o']
    req.get_subject().OU = CSR_CONFIG['subject_ou']
    req.get_subject().L = CSR_CONFIG['subject_l']
    req.get_subject().ST = CSR_CONFIG['subject_st']
    req.get_subject().C = CSR_CONFIG['subject_c']
    req.get_subject().emailAddress = CSR_CONFIG['subject_email']
    req.set_pubkey(key)
    req.sign(key, 'sha256')

    csr_dump = dump_certificate_request(FILETYPE_PEM, req)

    # Write CSR and Key
    #with open(csr_file_path, 'wb+') as f:
    #    f.write(csr_dump)
    #with open(private_key_path, 'wb+') as f:
     #   f.write(dump_privatekey(FILETYPE_PEM, key))

    return csr_dump


def gen_csr(domain):
    os.chdir(sys.path[0])
    csr_file_path = CSR_CONFIG['csr_file_path'] + domain + ".csr"
    key_file_path = CSR_CONFIG['key_file_path'] + domain + ".key"
    csr_dump = create_csr(domain, csr_file_path, key_file_path)
    #print(csr_dump)
    return csr_dump