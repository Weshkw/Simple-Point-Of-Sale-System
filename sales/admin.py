from django.contrib import admin

from .models import CancelledSale, Product, Sale


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_name", "product_price", "date_uploaded"]
    search_fields = ["product_name"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["sale_name", "sale_price", "user", "sale_date"]
    list_filter = ["sale_date"]
    list_select_related = ["user"]
    search_fields = ["sale_name", "user__username"]


@admin.register(CancelledSale)
class CancelledSaleAdmin(admin.ModelAdmin):
    list_display = ["product_name", "cancelled_sale_price", "user", "cancelled_sale_date"]
    list_filter = ["cancelled_sale_date"]
    list_select_related = ["user"]
    search_fields = ["product_name", "cancellation_reason", "user__username"]
