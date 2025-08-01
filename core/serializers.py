from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Job, JobTask, Equipment
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed, ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'TECHNICIAN')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if not user.is_active:
            raise AuthenticationFailed('User account is inactive.', code='inactive_user')
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                {'error': 'Username and password are required.'},
                code='missing_fields'
            )

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed(
                'Invalid username or password.',
                code='invalid_credentials'
            )

        data = super().validate(attrs)
        return data

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'serial_number', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_serial_number(self, value):
        if Equipment.objects.filter(serial_number=value).exists():
            raise ValidationError('Serial number must be unique.')
        return value

class JobSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='TECHNICIAN'), source='assigned_to', write_only=True
    )

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'client_name', 'created_by', 'assigned_to', 'assigned_to_id', 'status', 'priority', 'scheduled_date', 'overdue', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        attrs['created_by'] = self.context['request'].user
        return attrs

class JobTaskSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), source='job', write_only=True
    )
    required_equipment = EquipmentSerializer(many=True, read_only=True)
    required_equipment_ids = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(), many=True, write_only=True, source='required_equipment'
    )

    class Meta:
        model = JobTask
        fields = ['id', 'job', 'job_id', 'title', 'description', 'status', 'order', 'required_equipment', 'required_equipment_ids', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        if 'job' in attrs and attrs['job'].assigned_to != self.context['request'].user and self.context['request'].user.role != 'ADMIN':
            raise ValidationError('You can only modify tasks for jobs assigned to you.')
        return attrs

class DashboardJobSerializer(serializers.ModelSerializer):
    tasks = JobTaskSerializer(many=True, read_only=True, source='jobtask_set')
    task_count = serializers.IntegerField(source='jobtask_set.count', read_only=True)
    completed_tasks = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'client_name', 'status', 'priority', 'scheduled_date', 'overdue', 'task_count', 'completed_tasks', 'tasks']

    def get_completed_tasks(self, obj):
        return obj.jobtask_set.filter(status='COMPLETED').count()