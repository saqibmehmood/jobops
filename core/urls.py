from django.urls import path
from .views import SignupView, CustomTokenObtainPairView, TechnicianDashboardView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('technician-dashboard/', TechnicianDashboardView.as_view(), name='technician-dashboard'),
]