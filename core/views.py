from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, JobSerializer, JobTaskSerializer, EquipmentSerializer, DashboardJobSerializer
from .permissions import IsAdmin, IsTechnician, IsSalesAgent
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from .models import Job, JobTask, Equipment

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello, {request.user.username} ({request.user.role})!"})

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

class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['status', 'priority', 'overdue']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin() | IsSalesAgent()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TECHNICIAN':
            return Job.objects.filter(assigned_to=user)
        return Job.objects.all()

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAdmin]

class JobTaskListCreateView(generics.ListCreateAPIView):
    queryset = JobTask.objects.all()
    serializer_class = JobTaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['status', 'job']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TECHNICIAN':
            return JobTask.objects.filter(job__assigned_to=user)
        return JobTask.objects.all()

class JobTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobTask.objects.all()
    serializer_class = JobTaskSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin() | IsTechnician()]
        return [IsAuthenticated()]

class EquipmentListCreateView(generics.ListCreateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['type', 'is_active']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

class EquipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAdmin]

class TechnicianDashboardView(generics.ListAPIView):
    permission_classes = [IsTechnician]
    serializer_class = DashboardJobSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['status', 'priority', 'overdue']

    def get_queryset(self):
        return Job.objects.filter(assigned_to=self.request.user).prefetch_related('jobtask_set__required_equipment')