from rest_framework import serializers
from .models import User, Account, AccountTransaction, Card, CardTransaction, Company, Paymentway

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


class CreateAccountSerializer(serializers.Serializer):
    country = serializers.CharField()
    currencyName = serializers.CharField()
    currencycode = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountTransaction
        fields = "__all__"


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = "__all__"

class CardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardTransaction
        fields = "__all__"

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "address1",
            "state",
            "city",
            "zipCode",
            "nationality",
            "documentType",
            "ProofOfAddressDoc",
            "nidImagefront",
            "nidImageback",
            "dateOfBirth",
            "cityOfBirth",
            "countryOfBirth"
        ]

class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

class PaymentWaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paymentway
        fields = "__all__"


class FundsSerializer(serializers.Serializer):

    account = serializers.CharField()
    country = serializers.CharField()
    bank_name = serializers.CharField()
    account_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    amount = serializers.CharField()
    code = serializers.CharField()
    pin = serializers.CharField(write_only=True, max_length=4)


class RegisterSerializer(serializers.Serializer):
    country = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField()
    phoneNumber = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    transactionPin = serializers.CharField(min_length=4, max_length=4)
    refCode = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        from .models import User

        if User.objects.filter(email=value).exists():
            raise ValueError("Email already exists")

        return value

    def validate_phoneNumber(self, value):
        from .models import User

        if User.objects.filter(phoneNumber=value).exists():
            raise ValueError("Phone number already exists")

        return value