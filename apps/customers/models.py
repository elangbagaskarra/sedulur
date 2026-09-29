from django.db import models

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ("COMPANY", "Perusahaan"),
        ("INDIVIDUAL", "Perorangan"),
    ]

    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default="COMPANY",
    )

    name = models.CharField(
        max_length=150,
    )

    company_name = models.CharField(
        max_length=150,
        blank=True,
    )

    npwp = models.CharField(
        max_length=30,
        blank=True,
    )

    nik = models.CharField(
        max_length=30,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    pic_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="PIC",
    )

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=15,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
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
        ordering = ["name"]

    def save(self, *args, **kwargs):

        if not self.code:

            last_customer = (
                Customer.objects
                .order_by("-id")
                .first()
            )

            next_number = 1

            if last_customer and last_customer.code:

                try:
                    number = int(
                        last_customer.code.split("-")[-1]
                    )

                    next_number = number + 1

                except ValueError:
                    pass

            self.code = f"CUST-{next_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"