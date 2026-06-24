from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, BaseUserManager
from django.utils import timezone
from . import managers
from .utils import resize_image, rand_string_generator, generate_random_number
from django.utils import timezone
from dateutil.relativedelta import relativedelta

# Create your models here.

class BusinessUsers(models.Model):

    industryChioce = [
        ('advertising & media', 'Advertising & Media'),
        ('agriculture & farming', 'Agriculture & Farming'),
        ('automotive sales & leasing', 'Automotive Sales & Leasing'),
        ('constructure & engineering', 'Constructure & Engineering'),
        ('cryptocurrency exchange', 'Cryptocurrency Exchange'),
        ('cryptocurrency services', 'Cryptocurrency Services'),
        ('e-commerce', 'E-commerce'),
    ]

    typeChioce = [
        ("charity", 'Charity'),
        ("cooperative", 'Cooperative'),
        ("foundation", 'Foundation'),
        ("franchise", 'Franchise'),
        ("holding company", 'Holding Company'),
        ("joint venture", 'Joint Venture'),
        ("limited liability company", 'Limited Liability Company'),
        ("multinational corporation", 'Multinational Corporation'),
    ]

    purposeChioce = [
        ('sending and receiving funds for business services ', 'Sending and receiving funds for business services '),
        ('paying staffs', 'Paying staffs'),
        ('holding FX to protect business profit from currency fluctuations', 'Holding FX to protect business profit from currency fluctuations'),
    ]

    name= models.CharField(null=False, blank=True, unique=True, max_length=200)
    email= models.EmailField(null=False, blank=True, unique=True)
    type= models.CharField(null=False, blank=True, max_length=1000, choices=typeChioce)
    createdDate= models.DateTimeField(default=timezone.now)
    industry= models.CharField(null=False, blank=True, max_length=1000, choices=industryChioce)
    purpose= models.TextField(name=False, blank=True, choices=purposeChioce)
    argrement= models.BooleanField(default=False)
    businessVerified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractUser):

    accountTypeChioces = [
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('fixed deposit', 'Fixed Deposit'),
        ('business', 'Business'),
        ('investment', 'investment')
    ]

    email= models.EmailField(verbose_name="user email", unique=True)
    middleName = models.CharField(unique=True, max_length=100, null=True, blank=True)
    token= models.CharField(max_length=100, unique=True, null=True, blank=True)
    avatar= models.FileField(verbose_name='useravatar', blank=True, null=True, upload_to="avatars/")
    avatarUrl= models.URLField(unique=True, null=True, blank=True)
    phoneNumber= models.BigIntegerField(unique=True, blank=True, null=True)
    country = models.CharField(null=True, blank=True, max_length=200)
    accountType = models.CharField(null=True, blank=True, choices=accountTypeChioces, default="savings")
    refCode = models.CharField(max_length=30, null=True, blank=True, unique=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    transactionPin = models.CharField(blank=True, null=True)

    #verified info 
    address1= models.TextField(null=True, blank=True)
    address2= models.TextField(null=True, blank=True)
    state = models.CharField(null=True, blank=True, max_length=500)
    city = models.CharField(null=True, blank=True, max_length=500)
    zipCode = models.BigIntegerField(null=True, blank=True)
    nationality = models.CharField(null=True, blank=True, max_length=200)
    documentType= models.CharField(null=True, blank=True, max_length=100)
    ProofOfAddressDoc = models.FileField(null=True, blank=True, upload_to="users/proof_of_address/")
    isVerifiedCompleted= models.IntegerField(default=0)
    nidImagefront = models.FileField(null=True, blank=True, unique=True, upload_to="users/NidImages/front/")
    nidImageback = models.FileField(null=True, blank=True, unique=True, upload_to="users/NidImages/back/")
    otp = models.IntegerField(null=True, blank=True, unique=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    is_saved = models.BooleanField(default=False)
    cityOfBirth = models.CharField(null=True, blank=True, max_length=300)
    countryOfBirth = models.CharField(null=True, blank=True, max_length=300)


    #linked info
    isBusinessAccount = models.OneToOneField(BusinessUsers, null=True, blank=True, unique=True, on_delete=models.PROTECT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['country']

    objects = managers.CustomUserManager()

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.is_saved == False:
            if self.avatar:
                self.avatar = resize_image(self.avatar, 180, 180)
                self.is_saved = True

        super().save(*args, **kwargs)

        if self.avatar:
            self.avatarUrl = self.avatar.url
            super().save(update_fields=["avatarUrl"])
    
class Account(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    country = models.CharField(max_length=200, null=True, blank=True)
    currencycode= models.CharField(max_length=2, null=True, blank=True)
    currencyName = models.CharField(max_length=100, null=True, blank=True)
    account_active = models.BooleanField(default=False)
    accountNumber = models.CharField(null=True, blank=True, unique=True, max_length=200)
    accountToken = models.CharField(null=True, blank=True, max_length=200, unique=True)
    achRoutingNumber = models.CharField(blank=True, null=True, unique=True, max_length=200)
    iban= models.CharField(null=True, blank=True, unique=True, max_length=100)
    sortCode = models.CharField(blank=True, null=True, unique=True, max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.country} --- Account"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            self.accountNumber = generate_random_number(10)
            self.accountToken = rand_string_generator(4)
            self.achRoutingNumber = generate_random_number(9)
            self.sortCode = generate_random_number(6)

        super().save(*args, **kwargs)

        if is_new:
            self.iban = f"{self.accountToken}{self.achRoutingNumber}{rand_string_generator(3)}"
            super().save(update_fields=["iban"])
        
class AccountTransaction(models.Model):

    transactionTypeChioce = [
        ("withdraw", "Withdraw"),
        ("deposit", "Deposit"),
        ("bills", "Bills"),
    ]

    statusChioce = [
        ("success", "Success"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    account = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE)
    currencySign= models.CharField(max_length=50, null=True, blank=True)
    amount= models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    type= models.CharField(max_length=50, null=True, blank=True, choices=transactionTypeChioce)
    destination= models.TextField(null=True, blank=True)
    status= models.CharField(max_length=50, null=True, blank=True, choices=statusChioce)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.account.user.first_name} transaction to {self.destination} -- {self.status}"
    
class Card(models.Model):

    cardTypeChioce = [
        ("visa", "Visa"),
        ("verve", "Verve"),
        ("mastercard", "MasterCard"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, null=True, blank=True, choices=cardTypeChioce)
    cardNumber = models.CharField(default=0, null=True, blank=True, unique=True, max_length=200)
    cvv = models.CharField(default=0, null=True, blank=True, unique=True, max_length=200)
    expiryDate = models.DateTimeField(null=True, blank=True)
    billingAddress = models.TextField(
        null=True,
        blank=True,
        default="651 N Broad Street, Suite 206, Middletown, DE 19700, United States"
    )
    zipcode = models.CharField(
        null=True,
        blank=True,
        default="19700",
        max_length=100
    )
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    frozen = models.BooleanField(default=False)
    createdDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} USD card"

    def save(self, *args, **kwargs):
        if not self.cardNumber:
            self.cardNumber = generate_random_number(16)

        if not self.cvv:
            self.cvv = generate_random_number(3)

        if not self.expiryDate:
            self.expiryDate = self.createdDate + relativedelta(years=2)

        super().save(*args, **kwargs)


class CardTransaction(models.Model):

    transactionTypeChioce = [
        ("withdraw", "Withdraw"),
        ("deposite", "Deposite"),
        ("bills", "Bills"),
    ]

    statusChioce = [
        ("success", "Success"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    card = models.ForeignKey(Card, null=False, blank=False, on_delete=models.CASCADE)
    currencySign= models.CharField(max_length=50, null=True, blank=True)
    amount= models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    type= models.CharField(max_length=50, null=True, blank=True, choices=transactionTypeChioce)
    destination= models.TextField(null=True, blank=True)
    status= models.CharField(max_length=50, null=True, blank=True, choices=statusChioce)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.account.user.first_name} transaction to {self.destination} -- {self.status}"
    
    class Meta:
        ordering = ["-created_at"]


class Company(models.Model):
    supportPhone= models.CharField(verbose_name="phone number with countrycode", null=False, blank=False, unique=True, max_length=20)
    supportEmail= models.EmailField(name=False, blank=False, unique=True)
    chatLink= models.URLField(verbose_name="whatsapp chat link", null=False, blank=False, unique=True)


    def __str__(self):
        return f"{self.supportEmail} -- company"


class Paymentway(models.Model):

    PaymentTypeChioce = [
        ("blockchain payment", "Blockchain Payment"),
        ("bank payment", "Bank Payment"),
    ]

    company = models.ForeignKey(Company, null=False, blank=False, on_delete=models.CASCADE)
    paymentType = models.CharField(null=True, blank=True, max_length=100, choices=PaymentTypeChioce)
    coinName = models.CharField(verbose_name="cryptocoin name or bankname if bank payment", null=False, blank=False, max_length=200)
    walletAddress= models.CharField(verbose_name="wallet address or bank account number", null=True, blank=True, max_length=5000, unique=True)
    tokenNetwork= models.CharField(null=True, blank=True, max_length=200)
    created_at= models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.company} --- paymentways"


 