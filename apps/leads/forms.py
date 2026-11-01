from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms import SpamProtectedForm

from .models import QuoteRequest, TemplateInquiry


class QuoteRequestForm(SpamProtectedForm):
    class Meta:
        model = QuoteRequest
        fields = [
            "name",
            "email",
            "phone",
            "company",
            "project_type",
            "budget",
            "timeline",
            "message",
            "attachment",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
            "attachment": forms.ClearableFileInput(
                attrs={"accept": ".pdf,.doc,.docx,.png,.jpg,.jpeg,.zip"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("project_type", "budget", "timeline"):
            self.fields[name].choices = [("", _("Choose…"))] + list(self.fields[name].choices)[1:]


class TemplateInquiryForm(SpamProtectedForm):
    class Meta:
        model = TemplateInquiry
        fields = ["name", "email", "phone", "business_name", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}
