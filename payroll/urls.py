from django.urls import path
from .views import AllSalaryHistoryAPIView, EmployeeHistoryAPIView, EmployeePayrollAPIView, EmployeeProfileAPIView, EmployeeSalaryUpdateAPIView, SalaryHistoryAPIView, EmployeeSalaryEffectiveAPIView, EmployeePayrollConsumptionAPIView, SalaryHistoryFilterAPIView
from .views import SalaryStructureGenerateAPIView, EmployeeCreateAPIView


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
    "employees/",
    EmployeeCreateAPIView.as_view(),
    name="employee-create"
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
    path(
    "employees/<str:employee_id>/salary-effective/",
    EmployeeSalaryEffectiveAPIView.as_view(),
    name="employee-salary-effective"
    ),
    path(
    "employees/<str:employee_id>/payroll-consumption/",
    EmployeePayrollConsumptionAPIView.as_view(),
    name="employee-payroll-consumption"
    ),
    path(
    "salary-history/",
    AllSalaryHistoryAPIView.as_view(),
    name="all-salary-history"
    ),
    path(
    "salary-history/filter/",
    SalaryHistoryFilterAPIView.as_view(),
    name="salary-history-filter"
    ),
]