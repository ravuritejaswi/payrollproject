from decimal import Decimal, ROUND_HALF_UP

from .salary_rules import (
    BASIC_PERCENTAGE,
    HRA_PERCENTAGE_OF_BASIC,
)


class SalaryStructureService:

    @staticmethod
    def round_amount(amount):
        return amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calculate_annual_ctc(lpa):
        return SalaryStructureService.round_amount(
            lpa * Decimal("100000")
        )

    @staticmethod
    def calculate_monthly_ctc(annual_ctc):
        return SalaryStructureService.round_amount(
            annual_ctc / Decimal("12")
        )

    @staticmethod
    def calculate_basic(monthly_ctc):
        return SalaryStructureService.round_amount(
            monthly_ctc * BASIC_PERCENTAGE
        )

    @staticmethod
    def calculate_hra(basic):
        return SalaryStructureService.round_amount(
            basic * HRA_PERCENTAGE_OF_BASIC
        )

    @staticmethod
    def calculate_remaining_allowance(
        monthly_ctc,
        basic,
        hra
    ):
        return SalaryStructureService.round_amount(
            monthly_ctc - basic - hra
        )

    @staticmethod
    def generate_salary_structure(lpa):

        # Step 1: Convert LPA to annual CTC
        annual_ctc = SalaryStructureService.calculate_annual_ctc(lpa)

        # Step 2: Convert annual CTC to monthly CTC
        monthly_ctc = SalaryStructureService.calculate_monthly_ctc(
            annual_ctc
        )

        # Step 3: Calculate Basic
        basic = SalaryStructureService.calculate_basic(
            monthly_ctc
        )

        # Step 4: Calculate HRA
        hra = SalaryStructureService.calculate_hra(
            basic
        )

        # Step 5: Calculate remaining monthly allowance
        special_allowance = (
            SalaryStructureService.calculate_remaining_allowance(
                monthly_ctc,
                basic,
                hra
            )
        )

        # Step 6: Verify monthly components
        total_monthly_components = (
            basic + hra + special_allowance
        )

        if total_monthly_components != monthly_ctc:
            raise ValueError(
                "Salary components do not reconcile with monthly CTC."
            )

        # Step 7: Calculate annual Basic
        annual_basic = SalaryStructureService.round_amount(
            basic * Decimal("12")
        )

        # Step 8: Calculate annual HRA
        annual_hra = SalaryStructureService.round_amount(
            hra * Decimal("12")
        )

        # Step 9: Calculate annual Special Allowance
        # as the remaining amount to guarantee
        # exact reconciliation with annual CTC.
        annual_special_allowance = (
            SalaryStructureService.round_amount(
                annual_ctc - annual_basic - annual_hra
            )
        )

        # Step 10: Verify annual components
        total_annual_components = (
            annual_basic
            + annual_hra
            + annual_special_allowance
        )

        if total_annual_components != annual_ctc:
            raise ValueError(
                "Annual salary components do not reconcile with annual CTC."
            )

        return {
            "annual_ctc": annual_ctc,
            "monthly_ctc": monthly_ctc,

            "salary_structure": {
                "basic": basic,
                "hra": hra,
                "special_allowance": special_allowance,
            },

            "annual_salary_structure": {
                "basic": annual_basic,
                "hra": annual_hra,
                "special_allowance": annual_special_allowance,
            },
        }