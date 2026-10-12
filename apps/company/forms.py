from django import forms

from .models import CompanySetting


class CompanySettingForm(forms.ModelForm):

    class Meta:
        model = CompanySetting

        fields = [
            "company_name",
            "address",
            "city",
            "phone",
            "email",
            "npwp",
            "logo",
            "bank_name",
            "bank_account_number",
            "bank_account_name",
            "default_currency",
            "invoice_prefix",
            "invoice_footer",
        ]

        widgets = {

            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama perusahaan",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Alamat perusahaan",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kota",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nomor telepon",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email perusahaan",
                }
            ),

            "npwp": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NPWP perusahaan",
                }
            ),

            "logo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "bank_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama bank",
                }
            ),

            "bank_account_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nomor rekening",
                }
            ),

            "bank_account_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nama pemilik rekening",
                }
            ),

            "default_currency": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "IDR",
                }
            ),

            "invoice_prefix": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "INV",
                }
            ),

            "invoice_footer": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Footer invoice",
                }
            ),
        }
class DatabaseRestoreForm(forms.Form):

    database_file = forms.FileField(
        label="File Database",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".sqlite3,.db",
            }
        ),
    )

    confirmation = forms.BooleanField(
        label="Saya memahami bahwa database saat ini akan diganti.",
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    def clean_database_file(self):

        file = self.cleaned_data[
            "database_file"
        ]

        allowed_extensions = (
            ".sqlite3",
            ".db",
        )

        filename = file.name.lower()

        if not filename.endswith(
            allowed_extensions
        ):
            raise forms.ValidationError(
                "File harus berformat .sqlite3 atau .db."
            )

        return file
        