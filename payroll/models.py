from django.db import models


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

# Create your models here.
