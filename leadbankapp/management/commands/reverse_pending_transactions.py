from django.core.management.base import BaseCommand
from leadbankapp.models import AccountTransaction
from datetime import timedelta
from django.utils import timezone
from leadbankapp.services import AccountSevice

class Command(BaseCommand):
    help = "Reverse pending transactions older than 24 hours"

    def handle(self, *args, **options):
        print("Cron is working!")

        cutoff = timezone.now() - timedelta(hours=24)

        transactions = AccountTransaction.objects.filter(status="pending", created_at__lte=cutoff)

        for transaction in transactions:
            AccountSevice.reverse_transaction(transaction)

        self.stdout.write(
            self.style.SUCCESS(
                f"Checked {transactions.count()} pending transaction(s)."
            )
        )
        