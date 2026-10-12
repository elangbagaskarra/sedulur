from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import (
    Invoice,
    InvoiceItem,
)

from apps.customers.models import Customer
from apps.products.models import Product
from apps.taxes.models import Tax


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice

        fields = [
            "customer",
            "invoice_date",
            "due_date",
            "currency",
            "tax_mode",
            "notes",
            "terms",
        ]

        widgets = {

            "customer": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "invoice_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "currency": forms.Select(
                choices=[
                    ("IDR", "IDR"),
                    ("USD", "USD"),
                ],
                attrs={
                    "class": "form-select",
                }
            ),

            "tax_mode": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder":
                        "Catatan invoice...",
                }
            ),

            "terms": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder":
                        "Syarat dan ketentuan...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "customer"
        ].queryset = (
            Customer.objects
            .filter(is_active=True)
            .order_by("name")
        )
def clean(self):

    cleaned_data = super().clean()

    invoice_date = cleaned_data.get(
        "invoice_date"
    )

    due_date = cleaned_data.get(
        "due_date"
    )

    if (
        invoice_date
        and due_date
        and due_date < invoice_date
    ):

        self.add_error(
            "due_date",
            (
                "Tanggal jatuh tempo "
                "tidak boleh sebelum "
                "tanggal invoice."
            ),
        )

    return cleaned_data

class InvoiceItemForm(
    forms.ModelForm
):

    class Meta:
        model = InvoiceItem

        fields = [
            "product",
            "quantity",
            "unit_price",
            "discount_percent",
            "tax",
        ]

        widgets = {

            "product": forms.Select(
                attrs={
                    "class":
                        "form-select item-product",
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class":
                        "form-control item-qty",
                    "min": "0.001",
                    "step": "0.001",
                }
            ),

            "unit_price":
                forms.NumberInput(
                    attrs={
                        "class":
                            "form-control item-price",
                        "min": "0",
                        "step": "0.01",
                    }
                ),

            "discount_percent":
                forms.NumberInput(
                    attrs={
                        "class":
                            "form-control item-discount",
                        "min": "0",
                        "max": "100",
                        "step": "0.01",
                    }
                ),

            "tax": forms.Select(
                attrs={
                    "class":
                        "form-select item-tax",
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "product"
        ].queryset = (
            Product.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields[
            "tax"
        ].queryset = (
            Tax.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields[
            "tax"
        ].required = False
def clean_quantity(self):

    quantity = self.cleaned_data.get(
        "quantity"
    )

    if quantity is not None and quantity <= 0:

        raise ValidationError(
            "Qty harus lebih dari 0."
        )

    return quantity


def clean_unit_price(self):

    price = self.cleaned_data.get(
        "unit_price"
    )

    if price is not None and price < 0:

        raise ValidationError(
            "Harga tidak boleh negatif."
        )

    return price


def clean_discount_percent(self):

    discount = self.cleaned_data.get(
        "discount_percent"
    )

    if discount is None:
        return 0

    if discount < 0 or discount > 100:

        raise ValidationError(
            "Diskon harus antara 0 sampai 100%."
        )

    return discount

InvoiceItemFormSet = (
    inlineformset_factory(
        Invoice,
        InvoiceItem,
        form=InvoiceItemForm,
        extra=1,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )
)