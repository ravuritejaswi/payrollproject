from decimal import Decimal

from rest_framework import serializers


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