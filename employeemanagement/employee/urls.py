from django.urls import path
from .views import ListCreateEmployeeAPIView, GetUpdateDeleteEmployeeDetails, LoginView, LogoutView, ChangePassword, \
    CreateVacationRequest, GetAllVacationRequests, UpdateVacationRequest

urlpatterns = [
    path('employee/', ListCreateEmployeeAPIView.as_view()),
    path('employee/<str:pk>/', GetUpdateDeleteEmployeeDetails.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('change-password/', ChangePassword.as_view()),
    path('request-vacation/<int:employee_id>/', CreateVacationRequest.as_view()),
    path('get-all-vacations/', GetAllVacationRequests.as_view()),
    path('update-vacation/<int:leave_id>/', UpdateVacationRequest.as_view()),
]