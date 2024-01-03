from django.contrib import admin
from .models import Product,Sale,CancelledSale

# Register your models here.

admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(CancelledSale)