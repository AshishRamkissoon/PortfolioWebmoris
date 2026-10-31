from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.contact, name="contact"),
    path("ready-made/<slug:slug>/", views.template_inquiry, name="template_inquiry"),
]
