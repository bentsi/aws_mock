import os
import sys
import uuid
import logging
from typing import TypeAlias
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime, timedelta
from functools import partial

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

from aws_mock.lib import strtobool


AWS_MOCK_CA_NAME = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "AWS Mock CA")])
AWS_MOCK_SERVER_NAME = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "AWS Mock Server")])
AWS_MOCK_ITSELF = "aws-mock.itself"
AWS_MOCK_DEFAULT_DIRNAME = "/etc/ssl/aws_mock"
AWS_MOCK_CA_CERTIFICATE_FILENAME = "ca/ca.crt"
AWS_MOCK_PRIVATE_KEY_FILENAME = "cert.key"

AWS_MOCK_HOSTS = os.environ.get("AWS_MOCK_HOSTS", "").split()
AWS_MOCK_SAVE_CA_KEY = strtobool(os.environ.get("AWS_MOCK_SAVE_CA_KEY", "false"))

DEBUG = strtobool(os.environ.get("DEBUG", "false"))
LOGGER = logging.getLogger(__name__)

PrivateKey: TypeAlias = rsa.RSAPrivateKey


def generate_passphrase(path: Path | None = None) -> bytes:
    LOGGER.debug("Generate random passphrase")
    passphrase = str(uuid.uuid4()).encode("ascii")
    if path:
        LOGGER.debug("Save passphrase to %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(passphrase)
    return passphrase


def generate_private_key(bits: int = 2048, path: Path | None = None, passphrase: bytes | None = None) -> PrivateKey:
    LOGGER.debug("Generate private key (bits=%d)", bits)
    key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    if path:
        LOGGER.debug("Save private key to %s", path)
        encryption = serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption,
        ))
    return key


def load_private_key(path: Path, passphrase: bytes | None = None) -> PrivateKey:
    LOGGER.debug("Load private key from %s", path)
    return serialization.load_pem_private_key(data=path.read_bytes(), password=passphrase)


def generate_ca_certificate(private_key: PrivateKey,
                            valid_for_days: int = 1825,
                            path: Path | None = None) -> x509.Certificate:
    LOGGER.debug("Generate CA certificate (valid for %d days)", valid_for_days)
    start_date = datetime.today() - timedelta(days=1)
    certificate = x509.CertificateBuilder(
        issuer_name=AWS_MOCK_CA_NAME,
        subject_name=AWS_MOCK_CA_NAME,
        public_key=private_key.public_key(),
        serial_number=x509.random_serial_number(),
        not_valid_before=start_date,
        not_valid_after=start_date + timedelta(days=valid_for_days),
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ).sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
    )
    if path:
        LOGGER.debug("Save CA certificate to %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(certificate.public_bytes(encoding=serialization.Encoding.PEM))
    return certificate


def load_certificate(path: Path) -> x509.Certificate:
    LOGGER.debug("Load certificate from %s", path)
    return x509.load_pem_x509_certificate(data=path.read_bytes())


def generate_csr(private_key: PrivateKey, path: Path | None = None) -> x509.CertificateSigningRequest:
    LOGGER.debug("Generate CSR")
    csr = x509.CertificateSigningRequestBuilder(
        subject_name=AWS_MOCK_SERVER_NAME
    ).sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
    )
    if path:
        LOGGER.debug("Save CSR to %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(csr.public_bytes(encoding=serialization.Encoding.PEM))
    return csr


def sign_csr(csr: x509.CertificateSigningRequest,  # pylint: disable=too-many-arguments
             ca_certificate: x509.Certificate,
             ca_private_key: PrivateKey,
             hosts: list[str],
             valid_for_days: int = 90,
             path: Path | None = None) -> x509.Certificate:
    LOGGER.debug("Generate signed certificate for %r (valid for %d days)", hosts, valid_for_days)
    start_date = datetime.today() - timedelta(days=1)
    certificate = x509.CertificateBuilder(
        issuer_name=ca_certificate.subject,
        subject_name=csr.subject,
        public_key=csr.public_key(),
        serial_number=x509.random_serial_number(),
        not_valid_before=start_date,
        not_valid_after=start_date + timedelta(days=valid_for_days),
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(host) for host in hosts]),
        critical=False,
    ).sign(
        private_key=ca_private_key,
        algorithm=hashes.SHA256(),
    )
    if path:
        LOGGER.debug("Save signed certificate to %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(certificate.public_bytes(encoding=serialization.Encoding.PEM))
    return certificate


def get_options(args: list[str] | None = None):
    parser = ArgumentParser(prog="python -m aws_mock.certificates")

    parser.add_argument("dirname", type=Path, nargs="?", default=AWS_MOCK_DEFAULT_DIRNAME)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--save-ca-private-key", action="store_true", default=AWS_MOCK_SAVE_CA_KEY)
    parser.add_argument("--ca-private-key", type=Path, metavar="PATH")
    passphrase = parser.add_mutually_exclusive_group()
    passphrase.add_argument("--passphrase", type=partial(bytes, encoding="utf-8"))
    passphrase.add_argument("--passphrase-file", type=Path, metavar="PATH")
    parser.add_argument("--save-csr", action="store_true")
    parser.add_argument("--csr", type=Path, metavar="PATH")
    parser.add_argument(
        "--add-host",
        action="append",
        type=str,
        dest="hosts",
        default=[AWS_MOCK_ITSELF],
        metavar="HOSTNAME",
    )
    parser.add_argument("--add-hosts-from-env", action="store_true")

    parsed_args = parser.parse_args(args=args)

    parsed_args.ca_certificate = parsed_args.dirname / AWS_MOCK_CA_CERTIFICATE_FILENAME
    parsed_args.private_key = parsed_args.dirname / AWS_MOCK_PRIVATE_KEY_FILENAME
    parsed_args.certificate = parsed_args.private_key.with_suffix(".crt")

    if parsed_args.ca_certificate.exists():
        LOGGER.debug("CA certificate found: %s", parsed_args.ca_certificate)
        if parsed_args.ca_private_key is None:
            parsed_args.ca_private_key = parsed_args.ca_certificate.with_suffix(".key")
            if parsed_args.ca_private_key.exists():
                LOGGER.debug("CA private key found: %s", parsed_args.ca_private_key)
            else:
                parser.error(
                    f"{parsed_args.ca_certificate} is already there, need to provide a path to the CA private key",
                )
        if parsed_args.passphrase is None and parsed_args.passphrase_file is None:
            parsed_args.passphrase_file = parsed_args.ca_certificate.with_suffix(".passphrase")
            if parsed_args.passphrase_file.exists():
                LOGGER.debug("Passphrase file for CA private key found: %s", parsed_args.passphrase_file)
            else:
                parser.error(f"{parsed_args.ca_certificate} is already there, need to provide a passphrase")

    if parsed_args.passphrase_file:
        LOGGER.debug("Load passphrase from %s", parsed_args.passphrase_file)
        parsed_args.passphrase = parsed_args.passphrase_file.read_bytes()

    if parsed_args.ca_private_key and not parsed_args.passphrase:
        parser.error(f"Need to provide a passphrase for {parsed_args.ca_private_key}")

    if parsed_args.add_hosts_from_env:
        parsed_args.hosts.extend(AWS_MOCK_HOSTS)

    LOGGER.debug("Parsed options: %s", parsed_args)

    return parsed_args


def main(args: list[str] | None = None) -> int:
    options = get_options(args=args)

    if options.ca_private_key:
        ca_private_key = load_private_key(path=options.ca_private_key, passphrase=options.passphrase)
    else:
        if options.passphrase is None:
            options.passphrase = generate_passphrase(
                path=options.ca_certificate.with_suffix(".passphrase") if options.save_ca_private_key else None,
            )
        ca_private_key = generate_private_key(
            path=options.ca_certificate.with_suffix(".key") if options.save_ca_private_key else None,
            passphrase=options.passphrase,
        )

    if options.ca_certificate.exists():
        ca_certificate = load_certificate(path=options.ca_certificate)
    else:
        ca_certificate = generate_ca_certificate(private_key=ca_private_key, path=options.ca_certificate)

    if options.csr:
        csr = load_certificate(path=options.csr)
    else:
        csr = generate_csr(
            private_key=generate_private_key(path=options.private_key),
            path=options.private_key.with_suffix(".csr") if options.save_csr else None,
        )

    sign_csr(
        csr=csr,
        ca_certificate=ca_certificate,
        ca_private_key=ca_private_key,
        hosts=options.hosts,
        path=options.certificate,
    )

    if not options.quiet:
        print(f"# AWS Mock CA certificate (saved to {options.ca_certificate})")
        print(options.ca_certificate.read_text())

        print(f"# AWS Mock server private key (saved to {options.private_key})")
        print(options.private_key.read_text())

        print(f"# AWS Mock server certificate (saved to {options.certificate})")
        print(options.certificate.read_text())

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        level=logging.DEBUG if DEBUG else logging.INFO,
    )
    sys.exit(main())
