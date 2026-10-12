from django import forms

from .models import Payment
from decimal import Decimal
from django.core.exceptions import ValidationError

class PaymentForm(forms.ModelForm):
    

    class Meta:
        model = Payment

        fields = [
            "payment_date",
            "amount",
            "method",
            "reference_number",
            "notes",
        ]

        widgets = {

            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "Nominal pembayaran",
                }
            ),

            "method": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "reference_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder":
                        "Nomor referensi / transfer",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder":
                        "Catatan pembayaran...",
                }
            ),
        }
        


def clean_amount(self):

    amount = self.cleaned_data.get(
        "amount"
    )

    if (
        amount is None
        or amount <= Decimal("0")
    ):

        raise ValidationError(
            "Nominal pembayaran harus lebih dari 0."
        )

    return amount
