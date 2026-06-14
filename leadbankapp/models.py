from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, BaseUserManager
from django.utils import timezone
from . import managers
from .utils import resize_image, rand_string_generator, generate_random_number

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
    createdDate= models.DateTimeField(auto_created=True)
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
    avatar= models.FileField(verbose_name='useravatar', unique=True, blank=True, null=True, upload_to="avatars/")
    avatarUrl= models.URLField(unique=True, null=True, blank=True)
    phoneNumber= models.BigIntegerField(unique=True, blank=True, null=True)
    country = models.CharField(null=True, blank=True)
    accountType = models.CharField(null=True, blank=True, choices=accountTypeChioces, default="savings")
    refCode = models.CharField(max_length=30, null=True, blank=True, unique=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    transactionPin = models.IntegerField(blank=True, null=True)

    #verified info 
    address1= models.TextField(null=True, blank=True)
    address2= models.TextField(null=True, blank=True)
    nidCard= models.BigIntegerField(null=True, blank=True, unique=True)
    ssnNumber= models.BigIntegerField(null=True, blank=True, unique=True)
    isVerifiedCompleted= models.IntegerField(default=0)
    nidImagefront = models.FileField(null=True, blank=True, unique=True, upload_to="users/NidImages/front/")
    nidImageback = models.FileField(null=True, blank=True, unique=True, upload_to="users/NidImages/back/")
    otp = models.IntegerField(null=True, blank=True, unique=True)

    #linked info
    isBusinessAccount = models.OneToOneField(BusinessUsers, null=True, blank=True, unique=True, on_delete=models.PROTECT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['country']

    objects = managers.CustomUserManager()

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.avatar:
            self.avatar = resize_image(self.avatar, 180, 180)

        super().save(*args, **kwargs)

        if self.avatar:
            self.avatarUrl = self.avatar.url
            super().save(update_fields=["avatarUrl"])
    
class Account(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    currencycode= models.CharField(max_length=2, null=True, blank=True)
    currencyName = models.CharField(max_length=100, null=True, blank=True)
    account_active = models.BooleanField(default=False)
    accountNumber = models.BigIntegerField(null=True, blank=True, unique=True)
    accountToken = models.CharField(null=True, blank=True, max_length=200, unique=True)
    achRoutingNumber = models.BigIntegerField(blank=True, null=True, unique=True)
    iban= models.CharField(null=True, blank=True, unique=True, max_length=100)
    sortCode = models.BigIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.user.first_name} --- Account"
    
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
        

    
    


