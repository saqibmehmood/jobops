from django.urls import path
from .views import TestAuthView, SignupView, CustomTokenObtainPairView

urlpatterns = [
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]