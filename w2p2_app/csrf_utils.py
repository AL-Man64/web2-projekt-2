import secrets

from django.http import HttpRequest
from django.utils.crypto import constant_time_compare


def issue_token(request: HttpRequest) -> str:
    token = request.session.get('custom_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        request.session['custom_csrf_token'] = token
    return token


def validate_token(request: HttpRequest, submitted: str | None) -> bool:
    expected = request.session.get('custom_csrf_token')
    ok = bool(expected and submitted) and constant_time_compare(expected, submitted)
    request.session.pop('custom_csrf_token', None)
    return ok
