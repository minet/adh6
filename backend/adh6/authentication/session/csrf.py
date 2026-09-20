"""Cookies are sent by the browser on its own, so requests that change data must prove they come from the app."""

from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
CSRF_HEADER = "X-Requested-With"
CSRF_HEADER_VALUE = "XMLHttpRequest"


def _is_cross_site(request: Request) -> bool:
    fetch_site = request.headers.get("Sec-Fetch-Site")
    if fetch_site is not None:
        return fetch_site not in {"same-origin", "none"}

    origin = request.headers.get("Origin")
    if origin is None:
        return False
    host = urlsplit("//" + request.headers.get("Host", "")).hostname
    return urlsplit(origin).hostname != host


def enforce_csrf_protection(request: Request) -> None:
    if request.method in SAFE_METHODS:
        return
    if request.headers.get(CSRF_HEADER) != CSRF_HEADER_VALUE or _is_cross_site(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-site request refused")
