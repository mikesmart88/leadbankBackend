from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from . import models
from .utils import get_total_balance_usd
from .serializers import AccountSerializer

User = get_user_model()

class AuthService:

    @staticmethod
    def login(request, email, password):
        
        check_user = User.objects.filter(email__iexact=email).first()

        if not check_user: 
            raise ValueError("User does not exits")
        
        user = authenticate(request, email=email, password=password)

        if not user:
            raise ValueError("Inavalid Credentials")
        
        if not user.status:
            raise ValueError("User does not exit")
        
        if not user.is_active:
            raise ValueError("Account Disabled")
        
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
    

class AccountSevice:

    @staticmethod
    def get_user_account_data(user):
        accounts = models.Account.objects.filter(user=user)

        return{
            "total_balance_usd": get_total_balance_usd(user),
            "accounts": AccountSerializer(accounts, many=True).data
        }