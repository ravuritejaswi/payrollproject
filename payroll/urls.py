from django.urls import path
from .views import EmployeePayrollAPIView
from .views import SalaryStructureGenerateAPIView


urlpatterns = [
    path(
        "salary-structure/generate/",
        SalaryStructureGenerateAPIView.as_view(),
        name="salary-structure-generate",
    ),
    path(
        "employee-payroll/",
        EmployeePayrollAPIView.as_view(),
        name="employee-payroll",
    ),
]