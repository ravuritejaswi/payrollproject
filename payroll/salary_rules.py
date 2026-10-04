from decimal import Decimal


BASIC_PERCENTAGE = Decimal("0.50")
HRA_PERCENTAGE_OF_BASIC = Decimal("0.50")
PF_EMPLOYEE_PERCENTAGE = Decimal("0.12")
PF_EMPLOYER_PERCENTAGE = Decimal("0.12")
PF_WAGE_CEILING = Decimal("15000")
EPS_PERCENTAGE = Decimal("0.0833")

ESI_EMPLOYEE_PERCENTAGE = Decimal("0.0075")
ESI_EMPLOYER_PERCENTAGE = Decimal("0.0325")
ESI_WAGE_CEILING = Decimal("21000")
ESI_DAILY_WAGE_EXEMPTION = Decimal("176")

# TDS - New Tax Regime
TDS_STANDARD_DEDUCTION = Decimal("75000")
TDS_HEALTH_EDUCATION_CESS = Decimal("0.04")

TDS_SLABS = [
    (Decimal("400000"), Decimal("0.00")),
    (Decimal("800000"), Decimal("0.05")),
    (Decimal("1200000"), Decimal("0.10")),
    (Decimal("1600000"), Decimal("0.15")),
    (Decimal("2000000"), Decimal("0.20")),
    (Decimal("2400000"), Decimal("0.25")),
    (Decimal("999999999"), Decimal("0.30")),
]

TDS_REBATE_LIMIT = Decimal("1200000")
TDS_REBATE_AMOUNT = Decimal("60000")