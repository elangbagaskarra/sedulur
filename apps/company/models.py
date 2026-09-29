from django.db import models


class CompanySetting(models.Model):
    company_name = models.CharField(
        max_length=150,
        default="PT Seduur Berkarys Grove",
    )

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    npwp = models.CharField(
        max_length=50,
        blank=True,
    )

    logo = models.ImageField(
        upload_to="company/",
        null=True,
        blank=True,
    )

    bank_name = models.CharField(
        max_length=100,
        blank=True,
    )

    bank_account_number = models.CharField(
        max_length=100,
        blank=True,
    )

    bank_account_name = models.CharField(
        max_length=150,
        blank=True,
    )

    default_currency = models.CharField(
        max_length=10,
        default="IDR",
    )

    invoice_prefix = models.CharField(
        max_length=20,
        default="INV",
    )

    invoice_footer = models.TextField(
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.company_name