from django.urls import path
from .views import EmployeeHistoryAPIView, EmployeePayrollAPIView, EmployeeProfileAPIView, EmployeeSalaryUpdateAPIView, SalaryHistoryAPIView
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
    path(
        "employees/<str:employee_id>/",
        EmployeeProfileAPIView.as_view(),
        name="employee-profile"
    ),
    path(
        "employees/<str:employee_id>/history/",
        EmployeeHistoryAPIView.as_view(),
        name="employee-history"
    ),

    path(
        "employees/<str:employee_id>/salary-history/",
        SalaryHistoryAPIView.as_view(),
        name="salary-history"
    ),

    path(
        "employees/<str:employee_id>/salary/",
        EmployeeSalaryUpdateAPIView.as_view(),
        name="employee-salary-update"
    ),
]