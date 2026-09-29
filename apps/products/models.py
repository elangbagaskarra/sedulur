from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
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
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ("GOODS", "Barang"),
        ("SERVICE", "Jasa"),
    ]

    sku = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default="GOODS",
    )

    description = models.TextField(
        blank=True,
    )

    unit = models.CharField(
        max_length=30,
        default="pcs",
    )

    sale_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    stock_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        default=0,
    )

    minimum_stock = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        default=0,
    )

    manage_stock = models.BooleanField(
        default=True,
    )

    taxable = models.BooleanField(
        default=True,
    )

    default_tax = models.ForeignKey(
        "taxes.Tax",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    is_active = models.BooleanField(
        default=True,
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
        return f"{self.sku} - {self.name}"


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ("IN", "Stok Masuk"),
        ("OUT", "Stok Keluar"),
        ("ADJUSTMENT", "Penyesuaian"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
    )

    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        validators=[MinValueValidator(0)],
    )

    stock_before = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        default=0,
    )

    stock_after = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        default=0,
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"