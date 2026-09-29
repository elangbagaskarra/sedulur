from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer

        fields = [
            "customer_type",
            "name",
            "company_name",
            "npwp",
            "nik",
            "email",
            "phone",
            "pic_name",
            "address",
            "city",
            "postal_code",
            "notes",
            "is_active",
        ]

        widgets = {

            "customer_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama pelanggan",
                }
            ),

            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama perusahaan",
                }
            ),

            "npwp": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NPWP",
                }
            ),

            "nik": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NIK",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "email@example.com",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "08xxxxxxxxxx",
                }
            ),

            "pic_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama PIC",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Alamat lengkap",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kota",
                }
            ),

            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kode pos",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Catatan tambahan...",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }