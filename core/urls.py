from django.urls import path
from .views import (
    TestAuthView, SignupView, CustomTokenObtainPairView,
    JobListCreateView, JobDetailView,
    JobTaskListCreateView, JobTaskDetailView,
    EquipmentListCreateView, EquipmentDetailView
)

urlpatterns = [
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('tasks/', JobTaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', JobTaskDetailView.as_view(), name='task-detail'),
    path('equipment/', EquipmentListCreateView.as_view(), name='equipment-list-create'),
    path('equipment/<int:pk>/', EquipmentDetailView.as_view(), name='equipment-detail'),
]