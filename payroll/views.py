from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SalaryStructureRequestSerializer
from .services import SalaryStructureService
from .serializers import EmployeePayrollSerializer
from .models import EmployeePayroll


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




class EmployeePayrollAPIView(APIView):

    def get(self, request):
        employees = EmployeePayroll.objects.all().order_by("-created_at")
        serializer = EmployeePayrollSerializer(
            employees,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeePayrollSerializer(
            data=request.data
        )

        if serializer.is_valid():
            employee = serializer.save()
            return Response(
                EmployeePayrollSerializer(employee).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# Create your views here.
