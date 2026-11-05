from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms import SpamProtectedForm
from apps.pricing.models import Package
from apps.readymade.models import WebsiteTemplate

from .models import QuoteRequest, TemplateInquiry


class QuoteRequestForm(SpamProtectedForm):
    """The project brief: what they need, about the business, features, style, budget, contact.

    Shown one step at a time with JavaScript, and as one ordinary form without it."""

    features = forms.MultipleChoiceField(
        label=_("What should it include?"),
        choices=[(key, label) for key, label in QuoteRequest.FEATURES.items()],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = QuoteRequest
        fields = [
            "project_type",
            "package",
            "company",
            "industry",
            "current_website",
            "pages",
            "features",
            "starting_template",
            "inspiration",
            "budget",
            "timeline",
            "message",
            "attachment",
            "name",
            "email",
            "phone",
        ]
        labels = {
            "project_type": _("What do you need?"),
            "package": _("Package you're interested in"),
            "company": _("Business name"),
            "industry": _("What does your business do?"),
            "current_website": _("Current website (if any)"),
            "pages": _("How many pages, roughly?"),
            "starting_template": _("Start from one of our demos?"),
            "inspiration": _("Websites you like (optional)"),
            "message": _("Anything else we should know?"),
        }
        help_texts = {
            "inspiration": _("Paste a few links and tell us what you like about them."),
        }
        widgets = {
            "project_type": forms.RadioSelect,
            "inspiration": forms.Textarea(attrs={"rows": 3}),
            "message": forms.Textarea(attrs={"rows": 4}),
            "current_website": forms.URLInput(attrs={"placeholder": "https://"}),
            "attachment": forms.ClearableFileInput(
                attrs={"accept": ".pdf,.doc,.docx,.png,.jpg,.jpeg,.zip"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = False
        # Radio and checkbox choices are styled as cards in the template.
        self.fields["project_type"].widget.attrs["class"] = "sr-only peer"
        self.fields["features"].widget.attrs["class"] = "size-5 shrink-0 accent-neon-cyan"
        self.fields["project_type"].choices = list(self.fields["project_type"].choices)[1:]
        for name in ("budget", "timeline", "pages"):
            self.fields[name].choices = [("", _("Choose…"))] + list(self.fields[name].choices)[1:]
        self.fields["package"].queryset = Package.objects.published()
        self.fields["package"].empty_label = _("Not sure yet")
        self.fields["starting_template"].queryset = WebsiteTemplate.objects.published().exclude(
            demo_url=""
        )
        self.fields["starting_template"].empty_label = _("No, something new")
        if self.instance.features:
            self.initial.setdefault("features", self.instance.features.split(","))

    def clean_features(self):
        return ",".join(self.cleaned_data["features"])


class TemplateInquiryForm(SpamProtectedForm):
    class Meta:
        model = TemplateInquiry
        fields = ["name", "email", "phone", "business_name", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}
