from django.db import models
from django.db.models import Q
import uuid
## Create your models here.
class EmployeePayroll(models.Model):
    employee_id = models.CharField(
        max_length=50,
        unique=True
    )

    employee_name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    annual_ctc = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    monthly_ctc = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    basic = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    hra = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    special_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    employee_pf = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    employer_pf = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    employee_esi = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    employer_esi = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    annual_tds = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    monthly_tds = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.employee_id} - {self.employee_name}"



#models for Employee, EmployeeSalaryHistory and EmployeeChangeHistory. These models store information about employees, their salary history and changes made to their salary. The Employee model has fields for employee ID, name, email, joining date, designation, department and current salary. The EmployeeSalaryHistory model has fields for employee, CTC, effective from and to dates, reason for change and created by. The EmployeeChangeHistory model has fields for employee, field name, old and new values, effective date, changed at, changed by and change reason.
class Employee(models.Model):
    employee_id = models.CharField(
        max_length=50,
        unique=True
    )
    correlation_id = models.UUIDField(
    default=None,
    null=True,
    blank=True,
    editable=False
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    joining_date = models.DateField()

    designation = models.CharField(
        max_length=100
    )

    department = models.CharField(
        max_length=100
    )

    current_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.employee_id} - {self.name}"




#models for EmployeeSalaryHistory and EmployeeChangeHistory. These models store information about an employee's salary history and changes made to their salary. The EmployeeSalaryHistory model has fields for employee, CTC, effective from and to dates, reason for change and created by. The EmployeeChangeHistory model has fields for employee, field name, old and new values, effective date, changed at, changed by and change reason.
class EmployeeSalaryHistory(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="salary_history"
    )

    ctc = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    effective_from = models.DateField()

    effective_to = models.DateField(
        null=True,
        blank=True
    )

    reason = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        ordering = ["-effective_from"]

        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                condition=Q(effective_to__isnull=True),
                name="unique_active_salary_per_employee",
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.ctc} - "
            f"{self.effective_from}"
        )

class EmployeeChangeHistory(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="change_history"
    )

    field_name = models.CharField(
        max_length=100
    )

    old_value = models.TextField(
        blank=True
    )

    new_value = models.TextField(
        blank=True
    )

    effective_date = models.DateField()

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    changed_by = models.CharField(
        max_length=100,
        blank=True
    )

    change_reason = models.CharField(
        max_length=255,
        blank=True
    )
    correlation_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True
    )

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.field_name} - "
            f"{self.effective_date}"
        )
