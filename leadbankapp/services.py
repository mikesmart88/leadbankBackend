from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from . import models
from .utils import get_total_balance_usd
from .serializers import AccountSerializer, SupportSerializer, PaymentWaysSerializer
from django.db import transaction, IntegrityError
from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils import timezone
from .mailservice import send_mail

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
        AccountSevice.send_transaction_email(account.user, transaction)

        transaction.status = "reversed"
        transaction.created_at = timezone.now()
        transaction.save()

        AccountSevice.send_transaction_email(account.user, transaction)

    def send_transaction_email(user, transaction):
        send_mail(
        user.email, 
        f"""
<section
  style="
    width: 100%;
    height: fit-content;
    background-color: whitesmoke;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Work Sans', sans-serif;
    padding: 20px 10px;
    box-sizing:border-box;
  "
>
  <div
    style="
      width: 100%;
      height: auto;
      background-color: white;
      overflow: hidden;
      border-radius: 10px;
    "
  >
    <div
      style="
        padding: 30px;
        background-image: url('https://leadbankuniversal.com/assets/bg_image-BumasGER.jpg');
        background-repeat: no-repeat;
        background-position: center;
        background-size: cover;
        display: flex;
        align-items: center;
        color: white;
        overflow: hidden;
        max-height: 100px;
      "
    >
      <div
        style="
          width: 30px;
          height: fit-content;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          box-sizing: border-box;

        "
      >
        <img
          src="https://leadbankuniversal.com/assets/leadbank-icon-BbymAn6i.png"
          alt="leadbank icon image"
          style="
          width:100%;
          height: auto;
          object-fit:cover;
          min-width:100%;
          max-width:100%;
          "
        />
      </div>
      <h2
        style="
          font-weight: 700;
          letter-spacing: -1px;
          margin: 0px;
          color:#ffffff
        "
      >
        Leadbank
      </h2>
    </div>

    <div style="padding: 20px; color:#333333; letter-spacing:-0.5px; line-height:150%;">
        <small style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">Hello {user.first_name}</small>
        <h3>Your wallet has been funded successfully! 🤑</h3>
        <p style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">
  Your details are shown below:
<br>
<table style="width: 100%; background-color: #bebebe67; border-radius: 10px; border-spacing:0px">
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Transaction Type</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >{transaction.type}</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Amount</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >{transaction.currencySign}{transaction.amount:,.2f}</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Description</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >{transaction.destination}</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Refrence</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >#{transaction.id}</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Date & Time</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >{transaction.created_at.strftime("%-d-%-m-%y T %-I:%M%p").lower()}</td>
  </tr>
  <tr style="align-items:center; justify-content:space-between; width:100%;">
    <th style="padding: 10px 15px; text-align:left; width: 50%;border-bottom:1px solid #f5f5f5;  font-weight:500; font-size: 14px; line-height:32px; color:#4B5563;">Status</th>
     <td style="padding: 10px 15px; text-align:left; border-bottom:1px solid #f8f8f8; width: 50%;font-size: 14px; line-height:32px; color:#4B5563;" >{transaction.status}</td>
  </tr>
</table>

<p style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">
  If you didn't initiate this transaction, please contact our support team immediately, by sending an email to
  <br>
  <a style="color: #000;" href="mailto:support@leadbankuniversal.com">
    support@leadbankuniversal.com
  </a>
</p>

  </div>
  <br>
  <p style="margin:0 0 25px 0;font-size:13px;line-height:34px;color:#4B5563;text-align:center;">
    ©2026. Grey. All rights reserved.
  </p>
</section>
"""
        )

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