
from decimal import Decimal

from django.test import SimpleTestCase
from rest_framework.test import APITestCase
from .services import SalaryStructureService


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
# Create your tests here.
