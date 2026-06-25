from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

# Register your models here.

@admin.register(models.User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {
            "fields": ("isVerifiedCompleted", "transactionPin", "middleName", "phoneNumber", "country", "gender")
        }),
    )

    pass

# admin.site.register(models.User)
admin.site.register(models.Account)
admin.site.register(models.AccountTransaction)
admin.site.register(models.Card)
admin.site.register(models.Company)
admin.site.register(models.Paymentway)
admin.site.register(models.CardTransaction)
