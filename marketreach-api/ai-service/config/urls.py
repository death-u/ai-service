from django.http import JsonResponse
from django.urls import include, path


def not_found(request, exception=None):
    return JsonResponse(
        {"success": False, "message": "Resource not found", "errors": []}, status=404
    )


def server_error(request):
    return JsonResponse(
        {"success": False, "message": "Internal server error", "errors": []}, status=500
    )


handler404 = "config.urls.not_found"
handler500 = "config.urls.server_error"

urlpatterns = [
    path("", include("forecasting.urls")),
]
