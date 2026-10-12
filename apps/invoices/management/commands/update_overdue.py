from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.invoices.models import Invoice


class Command(BaseCommand):

    help = "Update status invoice yang sudah jatuh tempo."

    def handle(self, *args, **options):

        today = timezone.localdate()

        updated = (
            Invoice.objects
            .filter(
                due_date__lt=today,
                balance_due__gt=0,
                status__in=[
                    "UNPAID",
                    "PARTIAL",
                ],
            )
            .update(
                status="OVERDUE"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"{updated} invoice "
                    f"diubah menjadi jatuh tempo."
                )
            )
        )