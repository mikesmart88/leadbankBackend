from django.shortcuts import render
from .services import AuthService, AccountSevice, CardService, SupportService, UserServices
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
import json
from .serializers import LoginSerializer, UserInfoSerializer, UserUpdateSerializer, TransactionSerializer, CardSerializer, CardTransactionSerializer, VerificationSerializer, CreateAccountSerializer, FundsSerializer, RegisterSerializer
from . import models
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from datetime import date
from decimal import Decimal
from .mailservice import send_mail
from django.shortcuts import get_object_or_404



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
    
class SignupViews(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        try:
            serializer = RegisterSerializer(
                data=request.data
            )

            serializer.is_valid(raise_exception=True)

            user = AuthService.create_user(serializer.validated_data)

            if user:
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
          color:#333333
        "
      >
        Leadbank
      </h2>
    </div>

    <div style="padding: 20px; color:#333333; letter-spacing:-1px; line-height:150%;">
        <small style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563; text-transform: capitalize;">Hello {user.first_name}</small>
        <h3>Welcome to Leadbank 😃</h3>
        <p style="margin:0 0 25px 0;font-size:14px;line-height:32px;color:#4B5563;">
  At LeadBank, we believe banking should be secure, simple, and accessible. Whether you're saving, transferring funds, managing multiple currencies, or growing your financial future, we're here to provide the tools you need every step of the way.
</p>
<p style="margin:0 0 25px 0;font-size:14px;line-height:34px;color:#4B5563;">
    Now, sit back as we relieve you of every hassle that comes with international transactions.
</p>
  </div>
  <br>
  <p style="margin:0 0 25px 0;font-size:13px;line-height:34px;color:#4B5563;text-align:center;">
    ©2026. Grey. All rights reserved.
  </p>
</section>

                    """,
                    "Welcome to Leadbank",
                    f"{user.first_name} {user.last_name}"
                )

            return Response (
                {
                "success": "Account created successfully",
                "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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
    
    def post(self, request):

        try:
            # print("REQUEST DATA:", request.data)
            serializer = CreateAccountSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            password = serializer.validated_data["password"]

            # print("backend reached")

            user = AuthService.verify_password(request.user, password)

            if not user:
                return Response({
                    "message": "Incorrect Password"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            account = AccountSevice.create_account(
                user=request.user,
                data=serializer.validated_data
            )

            return Response({
                "success": "Bank Account created successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("ERROR:", str(e))

            return Response({
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class Transaction(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status = request.GET.get("status")

        Transactions = AccountSevice.get_user_transactions(request.user, status)
        serializer = TransactionSerializer(Transactions, many=True)

        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = FundsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            print("backend reached")

            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            amount = serializer.validated_data["amount"]
            code = serializer.validated_data["code"]
            pin = serializer.validated_data["pin"]
            fee = Decimal("0.20")

            new_amount = Decimal(amount) - fee

            pin = AuthService.verify_pin(request.user, pin)

            #verify pin
            if not pin:
                return Response({
                    "message": "Invalid transaction pin"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # check account balance
            account = models.Account.objects.filter(
                user=request.user, 
                currencyName=serializer.validated_data["account"]
                ).first()
            
            #check balance
            if account:
                if float(account.balance) < float(amount):
                    raise ValueError("Insufficient funds")
                pass

            #check if lead account
            recipient_isLead = models.Account.objects.filter(
                accountNumber__iexact=serializer.validated_data["account_number"]
            ).first()
            
            pass
            if not recipient_isLead:
                accountNumber = serializer.validated_data["account_number"]
                bankname = serializer.validated_data["bank_name"]
                destination = f"sent to {first_name} {last_name} | {accountNumber} | {bankname} "
                AccountSevice.account_debit(account, amount)
                transaction = AccountSevice.create_account_transaction(account, new_amount, "withdraw", destination, "pending")
                if transaction:
                    AccountSevice.send_transaction_email(account.user, transaction, "Funds sent it pending!", "Transaction Pending")
                pass

                return Response({
                "status": "pending",
                "amount": f"{code}{amount}",
                "recipient": f"{first_name} {last_name}",
                "date": date.today(),
                }, status=status.HTTP_200_OK)
            
            else:
                if recipient_isLead.currencyName != account.currencyName:
                    accountNumber = serializer.validated_data["account_number"]
                    bankname = serializer.validated_data["bank_name"]
                    destination = f"send to {first_name} {last_name} | {accountNumber} | {bankname} "
                    ftransaction = AccountSevice.create_account_transaction(account, new_amount, "withdraw", destination, "failed" )
                    if ftransaction:
                        AccountSevice.send_transaction_email(account.user, ftransaction, "Wallet transaction failed", "Transaction Failed")
                    pass

                    return Response({
                    "status": "failed",
                    "amount": f"{code}{amount}",
                    "recipient": f"{first_name} {last_name}",
                    "date": date.today(),
                    }, status=status.HTTP_200_OK)
                
                accountNumber = serializer.validated_data["account_number"]
                bankname = serializer.validated_data["bank_name"]

                destination = f"Sent to {first_name} {last_name} | {accountNumber} | {bankname} "
                destination2 = f"From {request.user.first_name} {request.user.last_name}"

                AccountSevice.account_debit(account, amount)
                me_transaction = AccountSevice.create_account_transaction(account, new_amount, "withdraw", destination, "success")
                if me_transaction:
                    AccountSevice.send_transaction_email(account.user, me_transaction, "Your funds have been sent successfully!!", "Funds Sent" )
                pass
                AccountSevice.account_top_up(recipient_isLead, amount)
                rtransaction = AccountSevice.create_account_transaction(recipient_isLead, new_amount, "Deposit", destination2, "success")
                if rtransaction:
                    AccountSevice.send_transaction_email(recipient_isLead.user, rtransaction, "Your wallet have been funded successfully", "Wallet funded successfully")
                pass
                return Response({
                    "status": "success",
                    "amount": f"{code}{amount}",
                    "recipient": f"{first_name} {last_name}",
                    "date": date.today(),
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("ERROR:", str(e))

            return Response({
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    

class CardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        card = CardService.get_card_data(request.user)

        if card is None:
            return Response({"error": "no card"}, status=404)

        serializer = CardSerializer(card)

        return Response(serializer.data)
    
    def patch(self, request):
        data = request.data.get("frozen")
        data = str(data).lower() == "true"
        print(data)
        card = models.Card.objects.filter(user=request.user).first()
        card.frozen = data
        card.save()

        if card.frozen == True:
            return Response({"message": "Card frozen"})
        else:
            return Response({"message": "Card unfrozen"})

    def delete(self, request):
        card = models.Card.objects.filter(user=request.user).first()

        if not card:
            return Response({"error": "No card found"}, status=404)

        account = AccountSevice.get_account_by_country(
            request.user,
            "United States"
        )

        if account:
            account.balance += 1
            account.save()

        card.delete()

        return Response({"message": "Card successfully deleted"})
    
    def post(self, request):
        try:
            card = CardService.create_card(request.user)
            serializer = CardSerializer(card)

            return Response(serializer.data)
        
        except ValueError as e:
            return Response(
                {"message": str(e)},
                status=400
            )
    
class CardTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cardtransaction = CardService.get_card_transaction(request.user)

        serializer = CardTransactionSerializer(cardtransaction, many=True)

        return Response(serializer.data)
    
class VerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerificationSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            user = serializer.save()

            user.isVerifiedCompleted = 5
            user.save()
            return Response(
                {"success": "Verification submitted"},
                status=status.HTTP_201_CREATED
            )
        
        print(serializer.errors) 
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SupportView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = SupportService.get_company_data()

            return Response(
                data,
                status=status.HTTP_200_OK
            )

        except ValueError as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        

class UpdateUserViews(APIView):
    permission_classes = [AllowAny]

    def put(self, request):
        try:
            serializer = UserUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            UserServices.Update_avatar(request.user, serializer.validated_data)

            return Response(
                {"success": "Avatar updated successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
                )
        

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limits = UserServices.get_account_limit(request.user)

        print(limits)

        return Response(limits)

            
        