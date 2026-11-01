from django import forms
from django.utils.translation import gettext_lazy as _

AUTOCOMPLETE = {"name": "name", "email": "email", "phone": "tel", "company": "organization"}


class SpamProtectedForm(forms.ModelForm):
    """Adds a honeypot: a field people never see, which bots tend to fill in.

    A filled honeypot is not reported as an error (that would tip the bot off);
    the view checks ``is_spam`` and quietly drops the submission instead.
    """

    website = forms.CharField(
        label=_("Leave this field empty"),
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in AUTOCOMPLETE:
                field.widget.attrs.setdefault("autocomplete", AUTOCOMPLETE[name])
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-input"
            if isinstance(field.widget, forms.ClearableFileInput):
                css = "form-file"
            field.widget.attrs.setdefault("class", css)

    @property
    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
