"""Síťové a souborové bezpečnostní invarianty."""

from __future__ import annotations

import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse

from .errors import PolicyError
from .paths import permission_bits

LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def is_loopback_host(host: str) -> bool:
    """True pouze pro doslovnou loopback adresu či localhost."""
    return host.casefold().rstrip(".") in LOOPBACK_HOSTS


def validate_public_https_url(url: str) -> str:
    """Odmítne credentials, lokální síť a neveřejné cíle research požadavku."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise PolicyError("Research dovoluje pouze veřejné HTTPS adresy.")
    if parsed.username or parsed.password:
        raise PolicyError("URL nesmí obsahovat přihlašovací údaje.")
    host = parsed.hostname.casefold().rstrip(".")
    if host in LOOPBACK_HOSTS or host.endswith(".local"):
        raise PolicyError("Lokální adresy nejsou pro research povoleny.")
    try:
        direct = ipaddress.ip_address(host)
        addresses = [direct]
    except ValueError:
        try:
            addresses = [
                ipaddress.ip_address(item[4][0])
                for item in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
            ]
        except socket.gaierror as exc:
            raise PolicyError("Doménu se nepodařilo bezpečně přeložit.") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise PolicyError("Research nesmí přistupovat do lokální ani privátní sítě.")
    return url


def is_private_path(path: Path, *, directory: bool) -> bool:
    """Ověří režim 700 pro adresář nebo 600 pro soubor."""
    expected = 0o700 if directory else 0o600
    return permission_bits(path) == expected
