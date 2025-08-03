from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, TechnicianDashboardSerializer
from .permissions import IsAdmin, IsTechnician
from .models import JobTask
from django.db.models import Q
from django.db.models.functions import TruncDate

class SignupView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'username': user.username,
                'email': user.email,
                'role': user.role
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class TechnicianDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTechnician]

    def get(self, request):
        # Get upcoming and in-progress tasks for the authenticated technician's jobs
        tasks = JobTask.objects.filter(
            Q(job__assigned_to=request.user) &
            (Q(status='UPCOMING') | Q(status='IN_PROGRESS'))
        ).annotate(
            date=TruncDate('job__scheduled_date')  # Group by Job.scheduled_date
        ).order_by('job__scheduled_date').prefetch_related('required_equipment')

        # Group tasks by date
        grouped_tasks = {}
        for task in tasks:
            date_str = task.date.strftime('%Y-%m-%d')
            if date_str not in grouped_tasks:
                grouped_tasks[date_str] = []
            grouped_tasks[date_str].append(task)

        # Serialize grouped data
        data = [
            {'date': date, 'tasks': tasks}
            for date, tasks in grouped_tasks.items()
        ]
        serializer = TechnicianDashboardSerializer(data, many=True)
        return Response(serializer.data)