from django.contrib import admin
from .models import EmployeePayroll

from .models import (
    EmployeePayroll,
    Employee,
    EmployeeSalaryHistory,
    EmployeeChangeHistory,
)
#admin class for EmployeePayroll model. It defines how the EmployeePayroll model is displayed and managed in the Django admin interface. It specifies the fields to be displayed in the list view, the fields that can be searched, and the default ordering of records.
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
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "name",
        "email",
        "joining_date",
        "designation",
        "department",
        "current_salary",
    )

    search_fields = (
        "employee_id",
        "name",
        "email",
    )

    ordering = (
        "-created_at",
    )

#admin class for EmployeeSalaryHistory model. It defines how the EmployeeSalaryHistory model is displayed and managed in the Django admin interface. It specifies the fields to be displayed in the list view, the fields that can be searched, and the default ordering of records.
@admin.register(EmployeeSalaryHistory)
class EmployeeSalaryHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "ctc",
        "effective_from",
        "effective_to",
        "reason",
        "created_by",
    )

    search_fields = (
        "employee__employee_id",
        "employee__name",
    )

    ordering = (
        "-effective_from",
    )


#admin class for EmployeeChangeHistory model. It defines how the EmployeeChangeHistory model is displayed and managed in the Django admin interface. It specifies the fields to be displayed in the list view, the fields that can be searched, and the default ordering of records.
@admin.register(EmployeeChangeHistory)
class EmployeeChangeHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "field_name",
        "old_value",
        "new_value",
        "effective_date",
        "changed_at",
        "changed_by",
    )

    search_fields = (
        "employee__employee_id",
        "employee__name",
        "field_name",
    )

    ordering = (
        "-changed_at",
    )

