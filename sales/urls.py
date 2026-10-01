from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sales/", views.sales_record, name="sales-record"),
    path("sales/<int:pk>/cancel/", views.cancel_sale, name="cancel-sale"),
    path("sales/cancelled/", views.cancelled_sales, name="cancelled-sales"),
]
