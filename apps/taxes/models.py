from django.db import models
from django.core.validators import MinValueValidator


class Tax(models.Model):
    TAX_TYPE_CHOICES = [
        ("PPN", "PPN"),
        ("PPH23", "PPh 23"),
        ("PPH_FINAL", "PPh Final"),
        ("OTHER", "Pajak Lainnya"),
    ]

    EFFECT_CHOICES = [
        ("ADD", "Menambah Total"),
        ("DEDUCT", "Mengurangi Total"),
    ]

    name = models.CharField(
        max_length=100,
    )

    code = models.CharField(
        max_length=30,
        unique=True,
    )

    tax_type = models.CharField(
        max_length=20,
        choices=TAX_TYPE_CHOICES,
    )

    rate = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(0)],
        help_text="Persentase pajak",
    )

    effect = models.CharField(
        max_length=10,
        choices=EFFECT_CHOICES,
        default="ADD",
    )

    is_active = models.BooleanField(
        default=True,
    )

    description = models.TextField(
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

    def __str__(self):
        return f"{self.name} ({self.rate}%)"