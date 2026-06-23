from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from . import models
from .utils import get_total_balance_usd
from .serializers import AccountSerializer, SupportSerializer, PaymentWaysSerializer
from django.db import transaction

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
    
    def verify_password(user, password):
        return authenticate(email=user.email, password=password)
    
    def verify_pin(user, pin):
        Pin = models.User.objects.filter(user=user, transactionPin__iexact=pin).first()
        if Pin:
            return True
        
        raise ValueError("Invalid transaction pin")
    

class AccountSevice:

    @staticmethod
    def get_user_account_data(user):
        accounts = models.Account.objects.filter(user=user)

        return{
            "total_balance_usd": get_total_balance_usd(user),
            "accounts": AccountSerializer(accounts, many=True).data
        }
    
    def get_user_transactions(user, status=None):
        queryset = models.AccountTransaction.objects.filter(account__user=user)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")
    
    def get_account_by_country(user, country):
        account = models.Account.objects.filter(
            user=user,
            country=country
        ).first()

        if account is None:
            raise ValueError("You have no US account available")

        return account
    

    def create_account(user, data):

    # 🔥 check if account already exists
        exists = models.Account.objects.filter(
            user=user,
            currencycode=data["currencycode"]
        ).exists()

        if exists:
            raise ValueError("You already have an account with this currency")

        # create account
        account = models.Account.objects.create(
            user=user,
            country=data["country"],
            currencyName=data["currencyName"],
            currencycode=data["currencycode"],
        )

        return account


    def create_account_transaction(user, amount, type, destination, status ):
        account = models.Account.objects.filter(user=user).first()
        if account:
            new_transaction = models.AccountTransaction.objects.create(
                account=account,
                currencySign=account.currencycode,
                amount=amount,
                type=type,
                destination=destination,
                status=status
            )

            new_transaction.save()

    

class CardService:
    @staticmethod
    @transaction.atomic
    def get_card_data(user):
        return models.Card.objects.filter(user=user).first()
    
    def get_card_transaction(user):

        card = models.Card.objects.filter(user=user).first()

        if card:
            transaction = models.CardTransaction.objects.filter(card=card).all()
            return transaction.order_by('-created_at')
        
    def create_card(user):
        account = AccountSevice.get_account_by_country(user, "United States")
        if account is None:
            raise ValueError("You have no US account available")
        
        if account.balance < 3:
            raise ValueError("Insufficient funds")
        
        new_card, created = models.Card.objects.get_or_create(user=user)

        if not created:
            raise ValueError("Card already exits")
        
        new_card.balance += 1
        account.balance -= 3
        account.save()
        new_card.save()

        return new_card
    
class SupportService:
    @staticmethod
    def get_company_data():
        company = models.Company.objects.first()

        if not company:
            return {
                "support": None,
                "paymentWays": []
            }

        payments = models.Paymentway.objects.filter(company=company).all()

        return {
            "support": SupportSerializer(company).data,
            "paymentWays": PaymentWaysSerializer(
                payments,
                many=True
            ).data
        }