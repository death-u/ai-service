"""
Turns every error into the team's standard response shape:

    {"success": false, "message": "...", "errors": [{"field": "...", "message": "..."}]}
"""
import logging

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

DEFAULT_MESSAGES = {
    400: "Request validation failed",
    401: "Authentication required or invalid",
    403: "Access forbidden",
    404: "Resource not found",
    405: "Method not allowed",
    415: "Unsupported media type; send application/json",
    429: "Too many requests",
}


def _flatten(detail, prefix):
    """Flatten DRF's nested error structure into [{field, message}, ...]."""
    errors = []
    if isinstance(detail, dict):
        for key, value in detail.items():
            if key == "non_field_errors":
                errors.extend(_flatten(value, prefix))
            elif isinstance(key, int) or str(key).isdigit():
                # Per-item errors of a list field, e.g. historicalSales[3]
                errors.extend(_flatten(value, f"{prefix}[{key}]"))
            else:
                errors.extend(_flatten(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(detail, list):
        for index, item in enumerate(detail):
            if isinstance(item, (dict, list)):
                errors.extend(_flatten(item, f"{prefix}[{index}]"))
            else:
                errors.append({"field": prefix, "message": str(item)})
    else:
        errors.append({"field": prefix, "message": str(detail)})
    return errors


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Unexpected crash: log it (without the request body) and hide internals.
        logger.exception("Unhandled error in forecasting service")
        return Response(
            {"success": False, "message": "Internal server error", "errors": []},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = response.status_code
    if isinstance(exc, ValidationError):
        errors = _flatten(exc.detail, "body")
        message = DEFAULT_MESSAGES[400]
    elif isinstance(exc, APIException):
        errors = []
        message = str(exc.detail) if code in (401, 403) else DEFAULT_MESSAGES.get(code, str(exc.detail))
    else:  # Http404 and PermissionDenied converted by DRF
        errors = []
        message = DEFAULT_MESSAGES.get(code, "Request failed")

    response.data = {"success": False, "message": message, "errors": errors}
    return response
