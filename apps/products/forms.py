from django import forms
from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama kategori",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Deskripsi kategori",
                }
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            "sku",
            "name",
            "category",
            "product_type",
            "description",
            "unit",
            "sale_price",
            "stock_quantity",
            "minimum_stock",
            "manage_stock",
            "taxable",
            "default_tax",
            "is_active",
        ]

        widgets = {
            "sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Contoh: PRD-001",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama produk / jasa",
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "product_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "unit": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "pcs / unit / jasa / jam",
                }
            ),

            "sale_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),

            "stock_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                }
            ),

            "minimum_stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.001",
                }
            ),

            "manage_stock": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "taxable": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "default_tax": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class StockAdjustmentForm(forms.Form):

    MOVEMENT_CHOICES = [
        ("IN", "Stok Masuk"),
        ("OUT", "Stok Keluar"),
        ("ADJUSTMENT", "Penyesuaian"),
    ]

    movement_type = forms.ChoiceField(
        choices=MOVEMENT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label="Jenis Pergerakan",
    )

    quantity = forms.DecimalField(
        max_digits=18,
        decimal_places=3,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.001",
                "placeholder": "Jumlah",
            }
        ),
    )

    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contoh: PO-001 / Pembelian",
            }
        ),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Catatan",
            }
        ),
    )