from decimal import Decimal
from rest_framework import serializers
from .services import SalaryStructureService

from .models import (
    EmployeePayroll,
    Employee,
    EmployeeSalaryHistory,
    EmployeeChangeHistory,
)

#It validates the data for SalaryStructureRequest model and serializes it to JSON format.
class SalaryStructureRequestSerializer(serializers.Serializer):
    lpa = serializers.DecimalField(
        required=True,
        max_digits=12,
        decimal_places=2
    )

    def validate_lpa(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError(
                "LPA must be greater than zero."
            )

        return value

#It validates the data for EmployeePayroll model and serializes it to JSON format.
class EmployeePayrollSerializer(serializers.ModelSerializer):
    lpa = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True
    )

    class Meta:
        model = EmployeePayroll
        fields = (
            "id",
            "employee_id",
            "employee_name",
            "email",
            "lpa",
            "annual_ctc",
            "monthly_ctc",
            "basic",
            "hra",
            "special_allowance",
            "employee_pf",
            "employer_pf",
            "employee_esi",
            "employer_esi",
            "annual_tds",
            "monthly_tds",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "annual_ctc",
            "monthly_ctc",
            "basic",
            "hra",
            "special_allowance",
            "employee_pf",
            "employer_pf",
            "employee_esi",
            "employer_esi",
            "annual_tds",
            "monthly_tds",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        lpa = validated_data.pop("lpa")

        payroll = SalaryStructureService.generate_salary_structure(
            lpa
        )

        salary = payroll["salary_structure"]
        pf = payroll["pf"]
        esi = payroll["esi"]
        tds = payroll["tds"]

        return EmployeePayroll.objects.create(
            **validated_data,

            annual_ctc=payroll["annual_ctc"],
            monthly_ctc=payroll["monthly_ctc"],

            basic=salary["basic"],
            hra=salary["hra"],
            special_allowance=salary["special_allowance"],

            employee_pf=pf["employee_pf"],
            employer_pf=pf["employer_pf"],

            employee_esi=esi["employee_esi"],
            employer_esi=esi["employer_esi"],

            annual_tds=tds["annual_tds"],
            monthly_tds=tds["monthly_tds"],
        )


#It validates the data for Employee model and serializes it to JSON format. It also validates the data for EmployeeSalaryHistory model and serializes it to JSON format.
class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "id",
            "employee_id",
            "name",
            "email",
            "joining_date",
            "designation",
            "department",
            "current_salary",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "current_salary",
            "created_at",
            "updated_at",
        )

#It validates the data for EmployeeSalaryHistory model and serializes it to JSON format.
class EmployeeSalaryHistorySerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = EmployeeSalaryHistory
        fields = (
            "id",
            "ctc",
            "effective_from",
            "effective_to",
            "reason",
            "created_at",
            "created_by",
        )


#It validates the data for EmployeeChangeHistory model and serializes it to JSON format.
class EmployeeChangeHistorySerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = EmployeeChangeHistory
        fields = (
            "id",
            "field_name",
            "old_value",
            "new_value",
            "effective_date",
            "changed_at",
            "changed_by",
            "change_reason",
            "correlation_id",
        )







