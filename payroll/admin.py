from django.contrib import admin
from .models import EmployeePayroll


@admin.register(EmployeePayroll)
class EmployeePayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "employee_name",
        "email",
        "annual_ctc",
        "monthly_ctc",
        "employee_pf",
        "employee_esi",
        "annual_tds",
    )

    search_fields = (
        "employee_id",
        "employee_name",
        "email",
    )

    ordering = (
        "-created_at",
    )

# Register your models here.
