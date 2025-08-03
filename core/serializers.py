from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Job, JobTask, Equipment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'is_active']

class JobTaskSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title')
    equipment = EquipmentSerializer(source='required_equipment', many=True)

    class Meta:
        model = JobTask
        fields = ['id', 'job_title', 'description', 'equipment', 'status']

class TechnicianDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()
    tasks = JobTaskSerializer(many=True)