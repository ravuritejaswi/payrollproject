from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SalaryStructureRequestSerializer
from .services import SalaryStructureService
from .serializers import EmployeePayrollSerializer
from .models import EmployeePayroll
from .history_services import SalaryHistoryService
from .models import (
    Employee,
    EmployeeSalaryHistory,
    EmployeeChangeHistory,
)

from .serializers import (
    EmployeeSerializer,
    EmployeeSalaryHistorySerializer,
    EmployeeChangeHistorySerializer,
)
## Create your views here.
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



#It handles the API requests for EmployeePayroll model. It allows to get the list of all employees and create a new employee payroll record.
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


#It handles the API requests for Employee model. It allows to get the details of a specific employee by their employee_id.
class EmployeeProfileAPIView(APIView):

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(
                employee_id=employee_id
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployeeSerializer(employee)

        return Response(serializer.data)

#employee creation api view
class EmployeeCreateAPIView(APIView):

    def post(self, request):
        serializer = EmployeeSerializer(
            data=request.data
        )

        if serializer.is_valid():
            employee = serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

#It handles the API requests for EmployeeSalaryHistory model. It allows to get the salary history of a specific employee by their employee_id.
class EmployeeHistoryAPIView(APIView):

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(
                employee_id=employee_id
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        history = (
            EmployeeChangeHistory.objects
            .filter(employee=employee)
            .order_by("-effective_date")
        )

        serializer = EmployeeChangeHistorySerializer(
            history,
            many=True
        )

        return Response({
            "employee_id": employee.employee_id,
            "history": serializer.data
        })

#It handles the API requests for EmployeeSalaryHistory model. It allows to get the salary history of a specific employee by their employee_id.
class SalaryHistoryAPIView(APIView):

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(
                employee_id=employee_id
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        history = (
            EmployeeSalaryHistory.objects
            .filter(employee=employee)
            .order_by("-effective_from")
        )

        serializer = EmployeeSalaryHistorySerializer(
            history,
            many=True
        )

        return Response({
            "employee_id": employee.employee_id,
            "salary_history": serializer.data
        })



#It handles the API requests for Employee model. It allows to get the details of a specific employee by their employee_id.
class EmployeeSalaryUpdateAPIView(APIView):

    def patch(self, request, employee_id):
        try:
            employee = Employee.objects.get(
                employee_id=employee_id
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_ctc = request.data.get("new_ctc")
        effective_from = request.data.get(
            "effective_from"
        )
        reason = request.data.get(
            "reason",
            ""
        )
        changed_by = request.data.get(
            "changed_by",
            ""
        )
        correlation_id = request.data.get(
            "correlation_id",
            ""
        )

        if not new_ctc:
            return Response(
                {"detail": "new_ctc is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not effective_from:
            return Response(
                {"detail": "effective_from is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from decimal import Decimal
            from datetime import date

            new_ctc = Decimal(str(new_ctc))
            effective_from = date.fromisoformat(
                effective_from
            )

            salary = SalaryHistoryService.update_salary(
                employee=employee,
                new_ctc=new_ctc,
                effective_from=effective_from,
                reason=reason,
                changed_by=changed_by,
                correlation_id=correlation_id
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            EmployeeSalaryHistorySerializer(
                salary
            ).data,
            status=status.HTTP_200_OK
        )


#It handles the API requests for EmployeeSalaryHistory model. It allows to get the salary effective on a specific date for a specific employee by their employee_id.
class EmployeeSalaryEffectiveAPIView(APIView):

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(
                employee_id=employee_id
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        target_date = request.query_params.get("date")

        if not target_date:
            return Response(
                {"detail": "date query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from datetime import date

            target_date = date.fromisoformat(
                target_date
            )

        except ValueError:
            return Response(
                {
                    "detail": (
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        salary = SalaryHistoryService.get_salary_for_date(
            employee=employee,
            target_date=target_date
        )

        if not salary:
            return Response(
                {
                    "detail": (
                        "No salary found for the requested date."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "employee_id": employee.employee_id,
                "effective_date": target_date,
                "ctc": salary.ctc,
                "salary_effective_from": salary.effective_from,
                "salary_effective_to": salary.effective_to,
            },
            status=status.HTTP_200_OK
        )


#It handles the API requests for EmployeePayroll model. It allows to get the payroll consumption for a specific employee by their employee_id and a specific payroll date.
class EmployeePayrollConsumptionAPIView(APIView):

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(
                employee_id=employee_id
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        payroll_date = request.query_params.get(
            "payroll_date"
        )

        if not payroll_date:
            return Response(
                {
                    "detail": (
                        "payroll_date query parameter is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from datetime import date

            payroll_date = date.fromisoformat(
                payroll_date
            )

        except ValueError:
            return Response(
                {
                    "detail": (
                        "Invalid payroll_date format. "
                        "Use YYYY-MM-DD."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payroll = (
                SalaryStructureService
                .calculate_payroll_for_date(
                    employee=employee,
                    payroll_date=payroll_date
                )
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            payroll,
            status=status.HTTP_200_OK
        )



