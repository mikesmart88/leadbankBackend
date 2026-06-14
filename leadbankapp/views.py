from django.shortcuts import render
from .services import AuthService, AccountSevice
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
import json
from .serializers import LoginSerializer, UserInfoSerializer
from . import models
from django.contrib.auth import get_user_model
from django.core.serializers import serialize



# Create your views here.
User = get_user_model()

class LoginViews(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = AuthService.login(
                request,
                serializer.validated_data["email"],
                serializer.validated_data["password"]
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response(
            {"success": "Login successful", **data},
            status=status.HTTP_200_OK
        ) 

class UserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserInfoSerializer(request.user)
        return Response(serializer.data)


class CheckSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user": {
                "id": request.user.id,
                "email": request.user.email,
            }
        })
    
class UserAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        return Response(
            AccountSevice.get_user_account_data(request.user)
        )