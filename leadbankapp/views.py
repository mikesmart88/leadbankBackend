from django.shortcuts import render
from .services import AuthService, AccountSevice, CardService, SupportService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
import json
from .serializers import LoginSerializer, UserInfoSerializer, TransactionSerializer, CardSerializer, CardTransactionSerializer, VerificationSerializer, CreateAccountSerializer, FundsSerializer
from . import models
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from datetime import date



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
                "success": "Reached backend successfully"
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
            recipient_isLead = account.objects.filter(
                accountNumber__iexact=serializer.validated_data["account_number"]
                ).first()
            if not recipient_isLead:
                accountNumber = serializer.validated_data["account_number"]
                bankname = serializer.validated_data["bank_name"]
                destination = f"sent to {first_name} {last_name} | {accountNumber} | {bankname} "
                AccountSevice.create_account_transaction(request.user, amount, "withdraw", destination, "pending")

            else:
                #create transaction date

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