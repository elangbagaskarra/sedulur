from django.db import models
from django.core.validators import MinValueValidator


class Payment(models.Model):
    METHOD_CHOICES = [
        ("CASH", "Tunai"),
        ("BANK_TRANSFER", "Transfer Bank"),
        ("QRIS", "QRIS"),
        ("CARD", "Kartu"),
        ("OTHER", "Lainnya"),
    ]

    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    method = models.CharField(
        max_length=30,
        choices=METHOD_CHOICES,
        default="BANK_TRANSFER",
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount}"