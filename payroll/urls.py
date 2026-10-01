from django.urls import path

from .views import SalaryStructureGenerateAPIView


urlpatterns = [
    path(
        "salary-structure/generate/",
        SalaryStructureGenerateAPIView.as_view(),
        name="salary-structure-generate",
    ),
]