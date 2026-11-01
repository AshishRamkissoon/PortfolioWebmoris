from django.urls import path

from . import views

app_name = "pricing"

urlpatterns = [
    path("", views.package_list, name="list"),
    path("<slug:slug>/checkout/", views.checkout, name="checkout"),
    path("order/<str:token>/", views.order_detail, name="order"),
    path("order/<str:token>/paypal/create/", views.paypal_create, name="paypal_create"),
    path("order/<str:token>/paypal/capture/", views.paypal_capture, name="paypal_capture"),
    path(
        "order/<str:token>/paypal/subscription/",
        views.paypal_subscription,
        name="paypal_subscription",
    ),
]
