from datetime import timedelta
from django.utils import timezone
from .models import AccountTransaction
from .services import AccountSevice

def reverse_expired_transactions():
    cutoff = timezone.now() - timedelta(hours=24)

    transactions = AccountTransaction.objects.filter(
        status="pending",
        created_at__lte=cutoff
    )

    for tx in transactions:
       AccountSevice.reverse_pending_transaction(tx)