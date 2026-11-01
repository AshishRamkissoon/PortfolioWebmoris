from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms import SpamProtectedForm

from .models import Order


def available_methods(package, site_settings):
    """Payment methods this package can actually be paid with right now."""
    methods = []
    if package.paypal_available:
        methods.append(Order.Method.PAYPAL)
    if site_settings.juice_number:
        methods.append(Order.Method.JUICE)
    if site_settings.bank_details:
        methods.append(Order.Method.BANK)
    return methods


class CheckoutForm(SpamProtectedForm):
    class Meta:
        model = Order
        fields = ["name", "email", "phone", "company", "notes_from_customer", "payment_method"]
        widgets = {
            "notes_from_customer": forms.Textarea(attrs={"rows": 3}),
            "payment_method": forms.RadioSelect,
        }
        labels = {"notes_from_customer": _("Anything we should know? (optional)")}

    def __init__(self, *args, methods, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields["payment_method"]
        field.choices = [
            (value, label) for value, label in Order.Method.choices if value in methods
        ]
        field.widget.attrs["class"] = "sr-only peer"  # styled as cards in the template
        if len(methods) == 1:
            field.initial = methods[0]


class ProofOfPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["transaction_ref", "proof_of_payment"]
        labels = {"transaction_ref": _("Transaction reference (from your Juice or bank receipt)")}
        widgets = {
            "proof_of_payment": forms.ClearableFileInput(
                attrs={"accept": ".pdf,.png,.jpg,.jpeg", "class": "form-file"}
            ),
            "transaction_ref": forms.TextInput(attrs={"class": "form-input"}),
        }

    def clean(self):
        data = super().clean()
        if not data.get("transaction_ref") and not data.get("proof_of_payment"):
            raise forms.ValidationError(
                _("Add your transaction reference or upload a screenshot of the payment.")
            )
        return data
