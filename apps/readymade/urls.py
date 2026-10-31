from django.urls import path

from . import views

app_name = "readymade"

urlpatterns = [
    path("", views.template_list, name="list"),
    path("<slug:slug>/", views.template_detail, name="detail"),
]
