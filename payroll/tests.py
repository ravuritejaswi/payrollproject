
from decimal import Decimal
from urllib import response
from django.test import TestCase
from django.test import SimpleTestCase
from rest_framework.test import APITestCase
from .services import SalaryStructureService
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


#Tests for SalaryStructureService class methods. It tests the calculation of annual CTC, monthly CTC, basic salary, HRA, special allowance, PF, ESI and TDS.
class SalaryStructureServiceTests(SimpleTestCase):

    def test_annual_ctc_for_6_lpa(self):
        result = SalaryStructureService.calculate_annual_ctc(
            Decimal("6")
        )

        self.assertEqual(
            result,
            Decimal("600000.00")
        )

    def test_monthly_ctc_for_6_lpa(self):
        annual_ctc = Decimal("600000")

        result = SalaryStructureService.calculate_monthly_ctc(
            annual_ctc
        )

        self.assertEqual(
            result,
            Decimal("50000.00")
        )

    def test_basic_is_50_percent_of_monthly_ctc(self):
        monthly_ctc = Decimal("50000")

        result = SalaryStructureService.calculate_basic(
            monthly_ctc
        )

        self.assertEqual(
            result,
            Decimal("25000.00")
        )

    def test_hra_is_50_percent_of_basic(self):
        basic = Decimal("25000")

        result = SalaryStructureService.calculate_hra(
            basic
        )

        self.assertEqual(
            result,
            Decimal("12500.00")
        )

    def test_remaining_allowance(self):
        monthly_ctc = Decimal("50000")
        basic = Decimal("25000")
        hra = Decimal("12500")

        result = (
            SalaryStructureService.calculate_remaining_allowance(
                monthly_ctc,
                basic,
                hra
            )
        )

        self.assertEqual(
            result,
            Decimal("12500.00")
        )

    def test_complete_salary_structure_for_6_lpa(self):
        result = SalaryStructureService.generate_salary_structure(
            Decimal("6")
        )

        self.assertEqual(
            result["annual_ctc"],
            Decimal("600000.00")
        )

        self.assertEqual(
            result["monthly_ctc"],
            Decimal("50000.00")
        )

        self.assertEqual(
            result["salary_structure"]["basic"],
            Decimal("25000.00")
        )

        self.assertEqual(
            result["salary_structure"]["hra"],
            Decimal("12500.00")
        )

        self.assertEqual(
            result["salary_structure"]["special_allowance"],
            Decimal("12500.00")
        )

#tests for SalaryStructureGenerateAPIView class. It tests the API endpoint for generating salary structure based on LPA input. It checks for valid and invalid inputs, and verifies the correctness of the generated salary structure.
class SalaryStructureAPITests(APITestCase):

    url = "/api/payroll/salary-structure/generate/"

    def test_valid_lpa_6(self):
        response = self.client.post(
            self.url,
            {"lpa": 6},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Decimal(str(response.data["annual_ctc"])),
            Decimal("600000.00")
        )

        self.assertEqual(
            Decimal(str(response.data["monthly_ctc"])),
            Decimal("50000.00")
        )

    def test_zero_lpa_rejected(self):
        response = self.client.post(
            self.url,
            {"lpa": 0},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_negative_lpa_rejected(self):
        response = self.client.post(
            self.url,
            {"lpa": -5},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_string_rejected(self):
        response = self.client.post(
            self.url,
            {"lpa": "abc"},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_lpa_rejected(self):
        response = self.client.post(
            self.url,
            {},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_decimal_lpa_accepted(self):
        response = self.client.post(
            self.url,
            {"lpa": 4.5},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Decimal(str(response.data["annual_ctc"])),
            Decimal("450000.00")
        )

        self.assertEqual(
            Decimal(str(response.data["monthly_ctc"])),
            Decimal("37500.00")
        )

    def test_multiple_lpa_values(self):

        test_cases = [
            (Decimal("3"), Decimal("300000.00"), Decimal("25000.00")),
            (Decimal("4.5"), Decimal("450000.00"), Decimal("37500.00")),
            (Decimal("6"), Decimal("600000.00"), Decimal("50000.00")),
            (Decimal("8"), Decimal("800000.00"), Decimal("66666.67")),
            (Decimal("10"), Decimal("1000000.00"), Decimal("83333.33")),
            (Decimal("12.5"), Decimal("1250000.00"), Decimal("104166.67")),
            (Decimal("20"), Decimal("2000000.00"), Decimal("166666.67")),
        ]

        for lpa, expected_annual, expected_monthly in test_cases:

            response = self.client.post(
                self.url,
                {"lpa": lpa},
                format="json"
            )

            self.assertEqual(response.status_code, 200)

            self.assertEqual(
                Decimal(str(response.data["annual_ctc"])),
                expected_annual
            )

            self.assertEqual(
                Decimal(str(response.data["monthly_ctc"])),
                expected_monthly
            )

    def test_salary_components_reconcile(self):

        test_cases = [
            Decimal("3"),
            Decimal("4.5"),
            Decimal("6"),
            Decimal("8"),
            Decimal("10"),
            Decimal("12.5"),
            Decimal("20"),
        ]

        for lpa in test_cases:

            response = self.client.post(
                self.url,
                {"lpa": lpa},
                format="json"
            )

            self.assertEqual(response.status_code, 200)

            structure = response.data["salary_structure"]

            basic = Decimal(str(structure["basic"]))
            hra = Decimal(str(structure["hra"]))
            special_allowance = Decimal(
                str(structure["special_allowance"])
            )

            monthly_ctc = Decimal(
                str(response.data["monthly_ctc"])
            )

            total_components = (
                basic
                + hra
                + special_allowance
            )

            self.assertEqual(
                total_components,
                monthly_ctc
            )

    def test_salary_structure_api_returns_pf_for_6_lpa(self):
        response = self.client.post(
            "/api/payroll/salary-structure/generate/",
            {"lpa": 6},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        pf = response.data["pf"]

        self.assertEqual(pf["pf_wage"], 15000.0)
        self.assertEqual(pf["employee_pf"], 1800.0)
        self.assertEqual(pf["employer_pf"], 1800.0)
        self.assertEqual(pf["eps"], 1249.5)

    def test_salary_structure_api_returns_pf_below_ceiling(self):
        response = self.client.post(
            "/api/payroll/salary-structure/generate/",
            {"lpa": 2.4},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        pf = response.data["pf"]

        self.assertEqual(pf["pf_wage"], 10000.0)
        self.assertEqual(pf["employee_pf"], 1200.0)
        self.assertEqual(pf["employer_pf"], 1200.0)
        self.assertEqual(pf["eps"], 833.0)

    def test_salary_structure_api_returns_esi_for_2_4_lpa(self):
        response = self.client.post(
            "/api/payroll/salary-structure/generate/",
            {"lpa": 2.4},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        esi = response.data["esi"]

        self.assertEqual(esi["esi_wage"], 20000.0)
        self.assertEqual(esi["employee_esi"], 150.0)
        self.assertEqual(esi["employer_esi"], 650.0)

    def test_salary_structure_api_esi_not_applicable_above_ceiling(self):
        response = self.client.post(
            "/api/payroll/salary-structure/generate/",
            {"lpa": 6},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        esi = response.data["esi"]

        self.assertEqual(esi["esi_wage"], 0.0)
        self.assertEqual(esi["employee_esi"], 0.0)
        self.assertEqual(esi["employer_esi"], 0.0)

    def test_salary_structure_api_returns_tds_for_15_lpa(self):
        response = self.client.post(
        "/api/payroll/salary-structure/generate/",
        {"lpa": 15},
        format="json"
        )

        self.assertEqual(response.status_code, 200)

        tds = response.data["tds"]

        self.assertEqual(tds["annual_income"], 1500000.0)
        self.assertEqual(tds["standard_deduction"], 75000.0)
        self.assertEqual(tds["taxable_income"], 1425000.0)
        self.assertEqual(tds["income_tax"], 93750.0)
        self.assertEqual(tds["rebate"], 0.0)
        self.assertEqual(tds["cess"], 3750.0)
        self.assertEqual(tds["annual_tds"], 97500.0)
        self.assertEqual(tds["monthly_tds"], 8125.0)

    def test_salary_structure_api_tds_rebate_for_10_lpa(self):
        response = self.client.post(
            "/api/payroll/salary-structure/generate/",
            {"lpa": 10},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        tds = response.data["tds"]

        self.assertEqual(tds["taxable_income"], 925000.0)
        self.assertEqual(tds["income_tax"], 32500.0)
        self.assertEqual(tds["rebate"], 32500.0)
        self.assertEqual(tds["cess"], 0.0)
        self.assertEqual(tds["annual_tds"], 0.0)
        self.assertEqual(tds["monthly_tds"], 0.0)

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="admin",
            password="admin12345"
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    

#tests for PF, ESI and TDS calculation methods in SalaryStructureService class. It tests the calculation of PF wage, employee PF, employer PF, EPS, ESI wage, employee ESI, employer ESI, taxable income, income tax and TDS rebate.
class PFCalculationTests(TestCase):

    def test_pf_wage_for_basic_below_ceiling(self):
        basic = Decimal("10000")

        pf_wage = SalaryStructureService.calculate_pf_wage(basic)

        self.assertEqual(pf_wage, Decimal("10000"))

    def test_pf_wage_for_basic_above_ceiling(self):
        basic = Decimal("25000")

        pf_wage = SalaryStructureService.calculate_pf_wage(basic)

        self.assertEqual(pf_wage, Decimal("15000"))

    def test_employee_pf_for_basic_above_ceiling(self):
        basic = Decimal("25000")

        employee_pf = SalaryStructureService.calculate_employee_pf(basic)

        self.assertEqual(employee_pf, Decimal("1800.00"))

    def test_employee_pf_for_basic_below_ceiling(self):
        basic = Decimal("10000")

        employee_pf = SalaryStructureService.calculate_employee_pf(basic)

        self.assertEqual(employee_pf, Decimal("1200.00"))

    def test_employer_pf_for_basic_above_ceiling(self):
        basic = Decimal("25000")

        employer_pf = SalaryStructureService.calculate_employer_pf(basic)

        self.assertEqual(employer_pf, Decimal("1800.00"))

    def test_eps_for_basic_above_ceiling(self):
        basic = Decimal("25000")

        eps = SalaryStructureService.calculate_eps(basic)

        self.assertEqual(eps, Decimal("1249.50"))

#tests for ESI calculation methods in SalaryStructureService class. It tests the calculation of ESI wage, employee ESI and employer ESI based on monthly wages and ESI wage ceiling.
class ESICalculationTests(TestCase):

    def test_esi_wage_below_ceiling(self):
        monthly_wages = Decimal("20000")

        esi_wage = SalaryStructureService.calculate_esi_wage(
            monthly_wages
        )

        self.assertEqual(esi_wage, Decimal("20000"))

    def test_esi_wage_at_ceiling(self):
        monthly_wages = Decimal("21000")

        esi_wage = SalaryStructureService.calculate_esi_wage(
            monthly_wages
        )

        self.assertEqual(esi_wage, Decimal("21000"))

    def test_esi_wage_above_ceiling(self):
        monthly_wages = Decimal("25000")

        esi_wage = SalaryStructureService.calculate_esi_wage(
            monthly_wages
        )

        self.assertEqual(esi_wage, Decimal("0.00"))

    def test_employee_esi_below_ceiling(self):
        monthly_wages = Decimal("20000")

        employee_esi = SalaryStructureService.calculate_employee_esi(
            monthly_wages
        )

        self.assertEqual(employee_esi, Decimal("150.00"))

    def test_employer_esi_below_ceiling(self):
        monthly_wages = Decimal("20000")

        employer_esi = SalaryStructureService.calculate_employer_esi(
            monthly_wages
        )

        self.assertEqual(employer_esi, Decimal("650.00"))

    def test_employee_esi_above_ceiling(self):
        monthly_wages = Decimal("25000")

        employee_esi = SalaryStructureService.calculate_employee_esi(
            monthly_wages
        )

        self.assertEqual(employee_esi, Decimal("0.00"))

    def test_employer_esi_above_ceiling(self):
        monthly_wages = Decimal("25000")

        employer_esi = SalaryStructureService.calculate_employer_esi(
            monthly_wages
        )

        self.assertEqual(employer_esi, Decimal("0.00"))

#tests for TDS calculation methods in SalaryStructureService class. It tests the calculation of taxable income, income tax and TDS rebate based on annual income and standard deduction.
class TDSCalculationTests(TestCase):

    def test_taxable_income_after_standard_deduction(self):
        annual_income = Decimal("1000000")

        taxable_income = (
            SalaryStructureService.calculate_taxable_income(
                annual_income
            )
        )

        self.assertEqual(
            taxable_income,
            Decimal("925000.00")
        )

    def test_taxable_income_cannot_be_negative(self):
        annual_income = Decimal("50000")

        taxable_income = (
            SalaryStructureService.calculate_taxable_income(
                annual_income
            )
        )

        self.assertEqual(
            taxable_income,
            Decimal("0.00")
        )

    def test_income_tax_for_925000(self):
        taxable_income = Decimal("925000")

        income_tax = (
            SalaryStructureService.calculate_income_tax(
                taxable_income
            )
        )

        self.assertEqual(
            income_tax,
            Decimal("32500.00")
        )

    def test_rebate_for_income_below_12_lakh(self):
        taxable_income = Decimal("925000")
        income_tax = Decimal("32500")

        rebate = SalaryStructureService.calculate_tds_rebate(
            taxable_income,
            income_tax
        )

        self.assertEqual(
            rebate,
            Decimal("32500.00")
        )

    def test_no_rebate_above_12_lakh(self):
        taxable_income = Decimal("1400000")
        income_tax = Decimal("150000")

        rebate = SalaryStructureService.calculate_tds_rebate(
            taxable_income,
            income_tax
        )

        self.assertEqual(
            rebate,
            Decimal("0.00")
        )

    def test_tds_for_10_lakh_income(self):
        result = SalaryStructureService.calculate_tds(
            Decimal("1000000")
        )

        self.assertEqual(
            result["taxable_income"],
            Decimal("925000.00")
        )

        self.assertEqual(
            result["income_tax"],
            Decimal("32500.00")
        )

        self.assertEqual(
            result["rebate"],
            Decimal("32500.00")
        )

        self.assertEqual(
            result["annual_tds"],
            Decimal("0.00")
        )

        self.assertEqual(
            result["monthly_tds"],
            Decimal("0.00")
        )

    def test_tds_for_15_lakh_income(self):
        result = SalaryStructureService.calculate_tds(
            Decimal("1500000")
        )

        self.assertEqual(
            result["taxable_income"],
            Decimal("1425000.00")
        )

        self.assertEqual(
            result["income_tax"],
            Decimal("93750.00")
        )

        self.assertEqual(
            result["rebate"],
            Decimal("0.00")
        )

        self.assertEqual(
            result["cess"],
            Decimal("3750.00")
        )

        self.assertEqual(
            result["annual_tds"],
            Decimal("97500.00")
        )

        self.assertEqual(
            result["monthly_tds"],
            Decimal("8125.00")
        )


