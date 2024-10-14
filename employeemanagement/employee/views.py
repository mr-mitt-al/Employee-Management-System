from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmployeeSerializer, ChangePasswordSerializer, RequestLeaveSerializer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Employee, RequestLeave
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from django.utils import timezone


class ListCreateEmployeeAPIView(APIView):
    """
    This View class will Create an Employee or List all the employees
    depending upon the http method. This view can only be accessed via
    Admin
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            initial_password = f"{employee.email}{employee.id}"
            employee.set_password(initial_password)
            employee.save()
            response_data = serializer.data
            response_data['initial_password'] = initial_password

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Remove pagination and return all employees directly
        employee_obj = Employee.objects.exclude(is_superuser=True)
        serializer = EmployeeSerializer(employee_obj, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetUpdateDeleteEmployeeDetails(APIView):
    """
     This View class will Update,Delete or List an Employee by providing ID
     depending upon the http method. This view can only be accessed via
     Admin
     """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        employee = get_object_or_404(Employee.objects.exclude(is_superuser=True), pk=pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        employee = get_object_or_404(Employee.objects.exclude(is_superuser=True), pk=pk)
        employee.delete()
        return Response({"message": "Employee deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        employee = get_object_or_404(Employee.objects.exclude(is_superuser=True), pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response({
                'refresh': str(refresh),
                'access': access,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.auth
            outstanding_token = OutstandingToken.objects.get(token=token)
            blacklisted_token = BlacklistedToken.objects.create(token=outstanding_token)
            return Response({"detail": "Successfully logged out."}, status=205)
        except OutstandingToken.DoesNotExist:
            return Response({"detail": "Token is invalid or has already been blacklisted."}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class CreateVacationRequest(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the authenticated employee from the request
        employee = request.user

        # Count the total approved leaves the employee has taken
        leaves_count = RequestLeave.objects.filter(employee=employee).count()

        if leaves_count >= 4:
            return Response({"error": "You have already requested the maximum number of leaves."},
                            status=status.HTTP_400_BAD_REQUEST)

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "Start and end dates are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert start and end dates to timezone-aware datetime objects
        try:
            start_date_obj = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date_obj = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the date range exceeds 2 days
        date_difference = (end_date_obj - start_date_obj).days
        if date_difference > 2:
            return Response({"error": "You cannot take more than 2 days leave at a time."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already has an overlapping leave request
        overlapping_leaves = RequestLeave.objects.filter(
            employee=employee,
            start_date__lte=end_date_obj,
            end_date__gte=start_date_obj
        ).exists()

        if overlapping_leaves:
            return Response({"error": "You already have a leave request during this period."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the leave request
        leave = RequestLeave.objects.create(
            employee=employee,
            start_date=start_date_obj,  # Save the timezone-aware datetime
            end_date=end_date_obj,      # Save the timezone-aware datetime
            attached_file=request.FILES.get('attached_file', None)
        )

        return Response({"message": "Leave requested successfully.", "leave_id": leave.id},
                        status=status.HTTP_201_CREATED)



class UpdateVacationRequest(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def post(self, request, leave_id):
        try:
            leave = RequestLeave.objects.get(id=leave_id)
        except RequestLeave.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        print(f"Current leave status: {leave.leave_status}, New status: {new_status}")

        leave.leave_status = new_status
        leave.save()

        return Response({"message": f"Leave request {new_status} successfully."}, status=status.HTTP_200_OK)


class GetAllVacationRequests(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        leave_requests = RequestLeave.objects.all()
        serializer = RequestLeaveSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeeVacationRequests(APIView):
    """
    API View to list all vacation requests made by the logged-in employee.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user
        vacation_requests = RequestLeave.objects.filter(employee=employee)
        serializer = RequestLeaveSerializer(vacation_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)