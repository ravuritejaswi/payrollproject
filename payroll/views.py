from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SalaryStructureRequestSerializer
from .services import SalaryStructureService


class SalaryStructureGenerateAPIView(APIView):

    def post(self, request):

        serializer = SalaryStructureRequestSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        lpa = serializer.validated_data["lpa"]

        salary_structure = (
            SalaryStructureService.generate_salary_structure(
                lpa
            )
        )

        response_data = {
            "input": {
                "lpa": lpa,
            },
            **salary_structure,
            "calculation_rules": {
                "basic": "50% of monthly CTC",
                "hra": "50% of basic",
                "special_allowance": "remaining amount",
            },
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )

# Create your views here.
