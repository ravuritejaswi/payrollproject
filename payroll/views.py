from urllib import request

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal
from .serializers import SalaryStructureRequestSerializer
from .services import SalaryStructureService
from .serializers import EmployeePayrollSerializer
from .models import EmployeePayroll
from .history_services import SalaryHistoryService
import uuid
import hashlib
import json

from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException

from .models import IdempotencyRecord

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

def get_request_hash(data):
    normalized_data = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        default=str
    )

    return hashlib.sha256(
        normalized_data.encode("utf-8")
    ).hexdigest()

#It handles the API requests for generating salary 
# structure based on the provided LPA (Lakhs Per Annum). 
# It validates the input LPA, generates the salary structure using the SalaryStructureService, 
# and returns the calculated salary components along with the input and calculation rules.
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



#It handles the API requests for EmployeePayroll model. It allows to get the list of all employees and create a new employee payroll record''''''
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
        
        idempotency_key = request.headers.get(
        "Idempotency-Key", ""
        ).strip()

        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())

        if len(idempotency_key) > 255:
            return Response(
        {
            "detail": (
                "Idempotency-Key must not exceed "
                "255 characters."
            )
        },
        status=status.HTTP_400_BAD_REQUEST
    )

        

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
        effective_from = request.data.get("effective_from")
        reason = request.data.get("reason", "")
        changed_by = request.data.get("changed_by", "")

        if new_ctc is None or new_ctc == "":
            return Response(
                {"detail": "new_ctc is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not effective_from:
            return Response(
                {"detail": "effective_from is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request_hash = get_request_hash({
            "employee_id": employee_id,
            "data": request.data,
        })

        try:
            with transaction.atomic():
                record, created = (
                    IdempotencyRecord.objects.get_or_create(
                        key=idempotency_key,
                        defaults={
                            "request_hash": request_hash,
                        },
                    )
                )

                if not created:
                    if record.request_hash != request_hash:
                        return Response(
                            {
                                "detail": (
                                    "This Idempotency-Key has "
                                    "already been used with "
                                    "a different request."
                                )
                            },
                            status=status.HTTP_409_CONFLICT
                        )

                    if record.response_body is None:
                        return Response(
                            {
                                "detail": (
                                    "This request is still "
                                    "being processed. Retry shortly."
                                )
                            },
                            status=status.HTTP_409_CONFLICT
                        )

                    return Response(
                        record.response_body,
                        status=record.response_status
                    )

                try:
                    new_ctc = Decimal(str(new_ctc))

                    from datetime import date
                    effective_from = date.fromisoformat(
                        effective_from
                    )

                    salary = SalaryHistoryService.update_salary(
                        employee=employee,
                        new_ctc=new_ctc,
                        effective_from=effective_from,
                        reason=reason,
                        changed_by=changed_by,
                        idempotency_key=idempotency_key,
                    )


                except ValueError as exc:
                    record.delete()
                    return Response(
                        {"detail": str(exc)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                response_body = (
                    EmployeeSalaryHistorySerializer(salary).data
                )

                record.response_status = status.HTTP_200_OK
                record.response_body = dict(response_body)
                record.save(
                    update_fields=[
                        "response_status",
                        "response_body",
                        "updated_at",
                    ]
                )

                return Response(
                    record.response_body,
                    status=record.response_status
                )

        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "A concurrent request used this key. "
                        "Retry using the same Idempotency-Key."
                    )
                },
                status=status.HTTP_409_CONFLICT
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

#all salary history api view
class AllSalaryHistoryAPIView(APIView):

    def get(self, request):

        salary_history = (
            EmployeeSalaryHistory.objects
            .select_related("employee")
            .order_by(
                "employee__employee_id",
                "-effective_from"
            )
        )

        result = {}

        for salary in salary_history:

            employee_id = salary.employee.employee_id

            if employee_id not in result:
                result[employee_id] = {
                    "employee_id": employee_id,
                    "employee_name": salary.employee.name,
                    "salary_history": []
                }

            result[employee_id]["salary_history"].append(
                EmployeeSalaryHistorySerializer(
                    salary
                ).data
            )

        return Response(
            list(result.values()),
            status=status.HTTP_200_OK
        )

#salary history filter api view
class SalaryHistoryFilterAPIView(APIView):

    def get(self, request):

        salary = request.query_params.get("salary")
        min_salary = request.query_params.get("min_salary")
        max_salary = request.query_params.get("max_salary")

        # Validate that at least one filter is provided
        if not salary and not min_salary and not max_salary:
            return Response(
                {
                    "detail": (
                        "Provide salary, or min_salary/max_salary."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Exact salary search
            if salary:

                salary = Decimal(str(salary))

                employees = Employee.objects.filter(
                    current_salary=salary
                )

            # Salary range search
            else:

                if min_salary:
                    min_salary = Decimal(str(min_salary))

                if max_salary:
                    max_salary = Decimal(str(max_salary))

                if (
                    min_salary is not None
                    and max_salary is not None
                    and min_salary > max_salary
                ):
                    return Response(
                        {
                            "detail": (
                                "min_salary cannot be greater "
                                "than max_salary."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                employees = Employee.objects.all()

                if min_salary is not None:
                    employees = employees.filter(
                        current_salary__gte=min_salary
                    )

                if max_salary is not None:
                    employees = employees.filter(
                        current_salary__lte=max_salary
                    )

        except (ValueError, TypeError):

            return Response(
                {
                    "detail": (
                        "Salary values must be valid numbers."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        employees = employees.order_by("employee_id")

        response_data = []

        for employee in employees:

            history = (
                EmployeeSalaryHistory.objects
                .filter(employee=employee)
                .order_by("-effective_from")
            )

            response_data.append(
                {
                    "employee_id": employee.employee_id,
                    "employee_name": employee.name,
                    "current_salary": employee.current_salary,
                    "salary_history": (
                        EmployeeSalaryHistorySerializer(
                            history,
                            many=True
                        ).data
                    )
                }
            )

        return Response(
            {
                "count": len(response_data),
                "employees": response_data
            },
            status=status.HTTP_200_OK
        )



