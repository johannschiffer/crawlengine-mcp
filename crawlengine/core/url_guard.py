"""
Outbound URL SSRF validator for CrawlEngine.
Blocks loopback, RFC1918 private addresses, link-local cloud metadata (169.254.169.254),
and non-HTTP(S) schemes unless CRAWLENGINE_ALLOW_PRIVATE_URLS=1 is set.
"""
import ipaddress
import os
import re
import socket
from typing import Tuple
from urllib.parse import urlparse

_BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
    "metadata.google.internal",
    "metadata",
}
_NUMERIC_HOST_RE = re.compile(r"^(0x[0-9a-f]+|\d+(\.\d+){0,3})$", re.IGNORECASE)


def _is_forbidden_ip(ip_obj: ipaddress._BaseAddress) -> bool:
    return (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def validate_crawl_url(url: str) -> Tuple[bool, str]:
    """Validate that a target URL uses HTTP(S) and does not point to internal infrastructure."""
    if not isinstance(url, str) or not url.strip():
        return False, "Invalid URL: empty target URL."

    raw = url.strip()
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        return False, f"Invalid URL scheme: '{raw}'. Must begin with http:// or https://"

    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        return False, "Invalid URL: missing hostname."

    if os.getenv("CRAWLENGINE_ALLOW_PRIVATE_URLS", "").strip() in ("1", "true", "yes"):
        return True, "Allowed by environment override."

    if host in _BLOCKED_HOSTS or host.endswith((".localhost", ".local", ".internal")):
        return False, f"Blocked target host '{host}': internal or loopback addresses are forbidden."

    try:
        ip_obj = ipaddress.ip_address(host)
        if _is_forbidden_ip(ip_obj):
            return False, f"Blocked target IP '{ip_obj}': non-public address range."
        return True, "Valid public IP."
    except ValueError:
        pass

    if _NUMERIC_HOST_RE.match(host):
        try:
            packed = socket.inet_aton(host)
            ip_obj = ipaddress.IPv4Address(packed)
            if _is_forbidden_ip(ip_obj):
                return False, f"Blocked target numeric IP '{ip_obj}': non-public address range."
        except OSError:
            return False, f"Blocked malformed numeric host '{host}'."

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return True, "Unresolved domain deferred to HTTP transport."

    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        addr_str = sockaddr[0].split("%", 1)[0]
        try:
            ip_obj = ipaddress.ip_address(addr_str)
        except ValueError:
            continue
        if _is_forbidden_ip(ip_obj):
            return False, f"Blocked target host '{host}': resolves to non-public IP '{ip_obj}'."

    return True, "Valid public URL."
