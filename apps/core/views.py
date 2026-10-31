from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"


class PlaceholderView(TemplateView):
    """Stand-in for pages that later phases build out."""

    template_name = "pages/placeholder.html"
    title = ""

    def get_context_data(self, **kwargs):
        return super().get_context_data(title=self.title, **kwargs)
