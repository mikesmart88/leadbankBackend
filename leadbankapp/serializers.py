from rest_framework import serializers
from .models import User, Account

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

