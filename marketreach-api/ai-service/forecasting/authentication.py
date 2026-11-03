"""
Service-to-service authentication.

The Node.js backend must send the shared secret in the `X-API-Key` header.
The comparison is constant-time and the service fails closed: if no key is
configured, every protected request is rejected.
"""
import hmac
import logging

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class ServiceUser:
    """Minimal stand-in user so DRF's permission checks work without a database."""

    is_authenticated = True
    is_active = True
    username = "node-backend"


class ApiKeyAuthentication(BaseAuthentication):
    header_meta_key = "HTTP_X_API_KEY"

    def authenticate(self, request):
        expected = settings.SERVICE_API_KEY
        if not expected:
            logger.error("SERVICE_API_KEY is not configured; rejecting request.")
            raise AuthenticationFailed("Service authentication is not configured.")

        provided = request.META.get(self.header_meta_key, "")
        if not provided or not hmac.compare_digest(provided.encode(), expected.encode()):
            raise AuthenticationFailed("Missing or invalid API key.")

        return (ServiceUser(), None)

    def authenticate_header(self, request):
        # Makes DRF answer 401 (not 403) when authentication fails.
        return "ApiKey"
