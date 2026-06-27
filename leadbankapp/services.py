from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from . import models
from .utils import get_total_balance_usd
from .serializers import AccountSerializer, SupportSerializer, PaymentWaysSerializer
from django.db import transaction, IntegrityError
from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()

class AuthService:

    @staticmethod
    def login(request, email, password):

        print("EMAIL:", email)

        check_user = User.objects.filter(email__iexact=email).first()
        print("CHECK USER:", check_user)

        if not check_user:
            raise ValueError("User does not exits")

        print("PASSWORD VALID:", check_user.check_password(password))

        user = authenticate(
            request,
            username=email,
            password=password
        )

        print("AUTH USER:", user)

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
        Pin = models.User.objects.filter(email=user.email, transactionPin__iexact=pin).first()
        if Pin:
            return True
        
        raise ValueError("Invalid transaction pin")
    
    def create_user(validated_data):

        user = models.User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.middleName = validated_data.get("middleName", "")
        user.gender = validated_data["gender"]
        user.phoneNumber = validated_data["phoneNumber"]
        user.country = validated_data["country"]
        user.transactionPin = validated_data["transactionPin"]

        user.save()

        # send welcome email here

        return user
    

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
    
    def account_debit(account, amount):
        account.balance -= Decimal(str(amount))
        account.save()

        return account
    
    def account_top_up(account, amount):
        amount = Decimal(str(amount))
        fee = Decimal("0.20")

        account.balance = account.balance + amount - fee
        account.save()

        return account

    def create_account(user, data):

        if user.isVerifiedCompleted != 5:
            raise ValueError("You need to verify your personals to create account")

        currency_code = data.get("currencycode")
        country = data.get("country")
        currency_name = data.get("currencyName")

        if not currency_code:
            raise ValueError("currencycode is required")

        if models.Account.objects.filter(user=user, currencycode=currency_code).exists():
            raise ValueError("You already have an account with this currency")

        try:
            with transaction.atomic():
                account = models.Account.objects.create(
                    user=user,
                    country=country,
                    currencyName=currency_name,
                    currencycode=currency_code,
                )
                return account

        except IntegrityError:
            raise ValueError("Account already exists")


    def create_account_transaction(account, amount, type, destination, status ):
        if account:
            new_transaction = models.AccountTransaction.objects.create(
                account=account,
                currencySign=account.currencycode,
                currency=account.currencyName,
                amount=amount,
                type=type,
                destination=destination,
                status=status
            )

            new_transaction.save()

    
    @staticmethod
    def reverse_transaction(transaction):
        if transaction.status != "pending" :
            pass

        if transaction.status != "reversed":
            pass

        account = transaction.account
        AccountSevice.account_top_up(account, transaction.amount)

        account.status = "reversed"
        account.save()

class CardService:
    @staticmethod
    @transaction.atomic
    def get_card_data(user):
        return models.Card.objects.filter(user=user).first()
    
    @staticmethod
    def get_card_transaction(user):

        card = models.Card.objects.filter(user=user).first()

        if card:
            transaction = models.CardTransaction.objects.filter(card=card).all()
            return transaction.order_by('-created_at')
        
    @staticmethod
    def create_card_transaction(user, amount, type, destination, status ):
        card = models.Card.objects.filter(user=user).first()
        if card:
            new_transaction = models.CardTransaction.objects.create(
                card=card,
                currencySign="$",
                amount=amount,
                type=type,
                destination=destination,
                status=status
            )

            new_transaction.save()
    @staticmethod
    def create_card(user):
        account = AccountSevice.get_account_by_country(user, "United States")
        if account is None:
            raise ValueError("You have no US account available")
        
        if account.balance < 3:
            raise ValueError("Insufficient funds")
        
        new_card, created = models.Card.objects.get_or_create(user=user)

        us_account = models.Account.objects.filter(user=user, country="United States").first()

        if not created:
            raise ValueError("Card already exits")
        
        new_card.balance += 1
        account.balance -= 3
        account.save()
        new_card.save()
        CardService.create_card_transaction(user, 1, "deposit", "Card creation Funding", "success")
        AccountSevice.create_account_transaction(account, 3, "withdraw", "Card service fee", "success")
        return new_card
    
class SupportService:
    @staticmethod
    def get_company_data():
        print("Service called")

        company = models.Company.objects.first()
        print("Company:", company)

        if not company:
            print("No company found")
            return {
                "support": None,
                "paymentWays": []
            }

        serializer = SupportSerializer(company)
        print("Serialized:", serializer.data)

        payments = models.Paymentway.objects.filter(company=company)

        return {
            "support": serializer.data,
            "paymentWays": PaymentWaysSerializer(
                payments,
                many=True
            ).data
        }