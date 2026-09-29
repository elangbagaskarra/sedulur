from django.db import models
from django.core.validators import MinValueValidator


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("UNPAID", "Belum Lunas"),
        ("PARTIAL", "Sebagian"),
        ("PAID", "Lunas"),
        ("OVERDUE", "Jatuh Tempo"),
        ("CANCELLED", "Dibatalkan"),
    ]

    TAX_MODE_CHOICES = [
        ("EXCLUSIVE", "Tax Exclusive"),
        ("INCLUSIVE", "Tax Inclusive"),
    ]

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    # Snapshot data customer
    customer_name = models.CharField(
        max_length=150,
    )

    customer_npwp = models.CharField(
        max_length=30,
        blank=True,
    )

    customer_address = models.TextField(
        blank=True,
    )

    invoice_date = models.DateField()

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
    )

    currency = models.CharField(
        max_length=10,
        default="IDR",
    )

    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=1,
    )

    tax_mode = models.CharField(
        max_length=20,
        choices=TAX_MODE_CHOICES,
        default="EXCLUSIVE",
    )

    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    discount_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    tax_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    withholding_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    grand_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    paid_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    balance_due = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    notes = models.TextField(
        blank=True,
    )

    terms = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-invoice_date", "-id"]

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items",
    )

    # Snapshot produk
    product_name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    unit = models.CharField(
        max_length=30,
        blank=True,
    )

    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        default=1,
        validators=[MinValueValidator(0)],
    )

    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    discount_percent = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    tax = models.ForeignKey(
        "taxes.Tax",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items",
    )

    # Snapshot pajak
    tax_name = models.CharField(
        max_length=100,
        blank=True,
    )

    tax_rate = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
    )

    tax_effect = models.CharField(
        max_length=10,
        blank=True,
    )

    line_subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product_name}"