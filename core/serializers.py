from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

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
        # Add custom claims (e.g., role)
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