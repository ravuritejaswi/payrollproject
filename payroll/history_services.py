from datetime import timedelta
from django.db import models, transaction


from .models import (
    Employee,
    EmployeeSalaryHistory,
    EmployeeChangeHistory,
)
#service class for handling salary history related operations. It provides methods to update an employee's salary, ensuring that the new salary does not overlap with existing salary periods, and to retrieve the salary for a specific date.
class SalaryHistoryService:

    @staticmethod
    @transaction.atomic
    def update_salary(
        employee,
        new_ctc,
        effective_from,
        reason="",
        changed_by=""
    ):
        if new_ctc <= 0:
            raise ValueError(
                "New CTC must be greater than zero."
            )

        if effective_from < employee.joining_date:
            raise ValueError(
                "Effective date cannot be before joining date."
            )

        active_salary = (
            EmployeeSalaryHistory.objects
            .filter(
                employee=employee,
                effective_to__isnull=True
            )
            .first()
        )
        overlapping_salary = (
            EmployeeSalaryHistory.objects
            .filter(
                employee=employee,
                effective_from__lte=effective_from,
            )
            .filter(
                models.Q(effective_to__gte=effective_from)
                | models.Q(effective_to__isnull=True)
            )
            .exclude(
                pk=active_salary.pk if active_salary else None
            )
            .first()
        )

        if overlapping_salary:
            raise ValueError(
                "Salary effective date overlaps with an existing salary period."
            )

        if active_salary:
            if effective_from <= active_salary.effective_from:
                raise ValueError(
                    "New effective date must be after the current salary effective date."
                )

            active_salary.effective_to = (
                effective_from - timedelta(days=1)
            )
            active_salary.save(
                update_fields=["effective_to"]
            )

            old_ctc = active_salary.ctc

        else:
            old_ctc = employee.current_salary

        new_salary = EmployeeSalaryHistory.objects.create(
            employee=employee,
            ctc=new_ctc,
            effective_from=effective_from,
            effective_to=None,
            reason=reason,
            created_by=changed_by,
        )

        employee.current_salary = new_ctc
        employee.save(
            update_fields=[
                "current_salary",
                "updated_at",
            ]
        )

        EmployeeChangeHistory.objects.create(
            employee=employee,
            field_name="salary",
            old_value=str(old_ctc),
            new_value=str(new_ctc),
            effective_date=effective_from,
            changed_by=changed_by,
            change_reason=reason,
        )

        return new_salary



    @staticmethod
    def get_salary_for_date(employee, target_date):
        salary = (
            EmployeeSalaryHistory.objects
            .filter(
                employee=employee,
                effective_from__lte=target_date,
            )
            .filter(
                models.Q(effective_to__gte=target_date)
                | models.Q(effective_to__isnull=True)
            )
            .order_by("-effective_from")
            .first()
        )

        return salary