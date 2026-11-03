from django.urls import re_path

from .views import HealthView, PredictDemandView

urlpatterns = [
    re_path(r"^api/v1/health/?$", HealthView.as_view(), name="health"),
    re_path(r"^api/v1/predict-demand/?$", PredictDemandView.as_view(), name="predict-demand"),
]
