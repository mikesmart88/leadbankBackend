from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Account)
admin.site.register(models.AccountTransaction)
admin.site.register(models.Card)
admin.site.register(models.Company)
admin.site.register(models.Paymentway)
