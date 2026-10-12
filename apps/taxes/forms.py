from decimal import Decimal

from django import forms

from .models import Tax


class TaxForm(forms.ModelForm):

    class Meta:
        model = Tax

        fields = [
            "name",
            "code",
            "tax_type",
            "rate",
            "effect",
            "is_active",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Contoh: PPN 11%",
                }
            ),

            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Contoh: PPN11",
                }
            ),

            "tax_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),

            "effect": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Keterangan pajak...",
                }
            ),
        }

    def clean_code(self):
        code = self.cleaned_data["code"]

        return code.strip().upper()

    def clean_rate(self):
        rate = self.cleaned_data["rate"]

        if rate < Decimal("0"):
            raise forms.ValidationError(
                "Tarif pajak tidak boleh negatif."
            )

        if rate > Decimal("100"):
            raise forms.ValidationError(
                "Tarif pajak tidak boleh lebih dari 100%."
            )

        return rate


class TaxCalculatorForm(forms.Form):

    TAX_MODE_CHOICES = [
        ("EXCLUSIVE", "Tax Exclusive"),
        ("INCLUSIVE", "Tax Inclusive"),
    ]

    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=0,
        label="Nominal",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "1000000",
            }
        ),
    )

    tax = forms.ModelChoiceField(
        queryset=Tax.objects.none(),
        label="Pajak",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    tax_mode = forms.ChoiceField(
        choices=TAX_MODE_CHOICES,
        label="Metode",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tax"].queryset = (
            Tax.objects
            .filter(is_active=True)
            .order_by("name")
        )