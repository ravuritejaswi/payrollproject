from decimal import Decimal, ROUND_HALF_UP

from .salary_rules import (
    BASIC_PERCENTAGE,
    HRA_PERCENTAGE_OF_BASIC,
    PF_EMPLOYEE_PERCENTAGE,
    PF_EMPLOYER_PERCENTAGE,
    PF_WAGE_CEILING,
    EPS_PERCENTAGE,
    ESI_EMPLOYEE_PERCENTAGE,
    ESI_EMPLOYER_PERCENTAGE,
    ESI_WAGE_CEILING,
    TDS_STANDARD_DEDUCTION,
    TDS_HEALTH_EDUCATION_CESS,
    TDS_SLABS,
    TDS_REBATE_LIMIT,
    TDS_REBATE_AMOUNT,
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
    def calculate_pf_wage(basic):
        return min(
            basic,
            PF_WAGE_CEILING
        )

    @staticmethod
    def calculate_employee_pf(basic):
        pf_wage = SalaryStructureService.calculate_pf_wage(basic)

        return SalaryStructureService.round_amount(
            pf_wage * PF_EMPLOYEE_PERCENTAGE
        )

    @staticmethod
    def calculate_employer_pf(basic):
        pf_wage = SalaryStructureService.calculate_pf_wage(basic)

        return SalaryStructureService.round_amount(
            pf_wage * PF_EMPLOYER_PERCENTAGE
        )

    @staticmethod
    def calculate_eps(basic):
        pf_wage = SalaryStructureService.calculate_pf_wage(basic)

        return SalaryStructureService.round_amount(
            pf_wage * EPS_PERCENTAGE
        )

    @staticmethod
    def calculate_esi_wage(monthly_wages):
        if monthly_wages > ESI_WAGE_CEILING:
            return Decimal("0.00")

        return monthly_wages

    @staticmethod
    def calculate_employee_esi(monthly_wages):
        esi_wage = SalaryStructureService.calculate_esi_wage(
            monthly_wages
        )

        if esi_wage == Decimal("0.00"):
            return Decimal("0.00")

        return SalaryStructureService.round_amount(
            esi_wage * ESI_EMPLOYEE_PERCENTAGE
        )

    @staticmethod
    def calculate_employer_esi(monthly_wages):
        esi_wage = SalaryStructureService.calculate_esi_wage(
            monthly_wages
        )

        if esi_wage == Decimal("0.00"):
            return Decimal("0.00")

        return SalaryStructureService.round_amount(
            esi_wage * ESI_EMPLOYER_PERCENTAGE
        )

    @staticmethod
    def calculate_taxable_income(annual_income):
        taxable_income = (
            annual_income - TDS_STANDARD_DEDUCTION
        )

        if taxable_income < Decimal("0.00"):
            taxable_income = Decimal("0.00")

        return SalaryStructureService.round_amount(
            taxable_income
        )

    @staticmethod
    def calculate_income_tax(taxable_income):
        tax = Decimal("0.00")
        previous_limit = Decimal("0.00")

        for upper_limit, rate in TDS_SLABS:
            if taxable_income <= previous_limit:
                break

            taxable_amount = min(
                taxable_income,
                upper_limit
            ) - previous_limit

            tax += taxable_amount * rate
            previous_limit = upper_limit

        return SalaryStructureService.round_amount(tax)

    @staticmethod
    def calculate_tds_rebate(
        taxable_income,
        income_tax
    ):
        if taxable_income <= TDS_REBATE_LIMIT:
            return min(
                income_tax,
                TDS_REBATE_AMOUNT
            )

        return Decimal("0.00")

    @staticmethod
    def calculate_tds(
        annual_income
    ):
        taxable_income = (
            SalaryStructureService.calculate_taxable_income(
                annual_income
            )
        )

        income_tax = (
            SalaryStructureService.calculate_income_tax(
                taxable_income
            )
        )

        rebate = (
            SalaryStructureService.calculate_tds_rebate(
                taxable_income,
                income_tax
            )
        )

        tax_after_rebate = income_tax - rebate

        cess = (
            tax_after_rebate
            * TDS_HEALTH_EDUCATION_CESS
        )

        annual_tds = (
            tax_after_rebate + cess
        )

        monthly_tds = (
            annual_tds / Decimal("12")
        )

        return {
            "annual_income": annual_income,
            "standard_deduction": TDS_STANDARD_DEDUCTION,
            "taxable_income": taxable_income,
            "income_tax": income_tax,
            "rebate": rebate,
            "tax_after_rebate": tax_after_rebate,
            "cess": SalaryStructureService.round_amount(
                cess
            ),
            "annual_tds": SalaryStructureService.round_amount(
                annual_tds
            ),
            "monthly_tds": SalaryStructureService.round_amount(
                monthly_tds
            ),
        }

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
        employee_pf = SalaryStructureService.calculate_employee_pf(basic)
        employer_pf = SalaryStructureService.calculate_employer_pf(basic)
        eps = SalaryStructureService.calculate_eps(basic)
        employee_esi = SalaryStructureService.calculate_employee_esi(monthly_ctc)
        employer_esi = SalaryStructureService.calculate_employer_esi(monthly_ctc)
        tds = SalaryStructureService.calculate_tds(annual_ctc)



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
            "pf": {
                "pf_wage": SalaryStructureService.calculate_pf_wage(basic),
                "employee_pf": employee_pf,
                "employer_pf": employer_pf,
                "eps": eps,
            },
            "esi": {
                "esi_wage": SalaryStructureService.calculate_esi_wage(
                monthly_ctc
                ),
            
                "employee_esi": employee_esi,
                "employer_esi": employer_esi,
            },
            "tds": tds,

            "annual_salary_structure": {
                "basic": annual_basic,
                "hra": annual_hra,
                "special_allowance": annual_special_allowance,
            },
        }