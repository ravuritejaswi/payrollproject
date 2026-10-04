from decimal import Decimal
from .models import EmployeePayroll
from rest_framework import serializers
from .services import SalaryStructureService


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