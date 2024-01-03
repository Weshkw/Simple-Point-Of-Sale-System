import os
import shutil
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_image = models.ImageField(upload_to='product_images/', blank=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_uploaded = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_name = models.CharField(max_length=200)
    sale_image = models.ImageField(upload_to='sale_images/', blank=True)
    sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.sale_name} on {self.sale_date}"
    
    def save(self, *args, **kwargs):
        # Copy the product image to the sale_images directory
        if self.product.product_image:
            source_path = os.path.join(settings.MEDIA_ROOT, str(self.product.product_image))
            destination_path = os.path.join(settings.MEDIA_ROOT, 'sale_images', os.path.basename(source_path))
            shutil.copyfile(source_path, destination_path)

            # Update the sale_image field with the copied image path
            self.sale_image.name = os.path.relpath(destination_path, settings.MEDIA_ROOT)

        super().save(*args, **kwargs)   

    def cancel_sale(self, cancellation_reason):
        # Create a CancelledSale instance with details from the current sale
        cancelled_sale = CancelledSale.objects.create(
            user=self.user,
            product_name=self.product.product_name,
            cancellation_reason=cancellation_reason,
            cancelled_sale_price=self.sale_price,
            cancelled_sale_date=self.sale_date
        )

        # Copy the sale image to the cancelled_sale_images directory
        if self.sale_image and os.path.exists(os.path.join(settings.MEDIA_ROOT, str(self.sale_image))):
            source_path = os.path.join(settings.MEDIA_ROOT, str(self.sale_image))
            destination_path = os.path.join(settings.MEDIA_ROOT, 'cancelled_sale_images', os.path.basename(source_path))
            shutil.copyfile(source_path, destination_path)

            # Update the cancelled_sale_image field with the copied image path
            cancelled_sale.cancelled_sale_image.name = os.path.relpath(destination_path, settings.MEDIA_ROOT)
            cancelled_sale.save()  # Save the cancelled_sale instance with the updated image path

        # Delete the current sale
        self.delete()

        return cancelled_sale

class CancelledSale(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    cancellation_reason = models.TextField()
    cancelled_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    cancelled_sale_image = models.ImageField(upload_to='cancelled_sale_images/', blank=True)
    cancelled_sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Cancelled Sale of {self.product_name} on {self.cancelled_sale_date}"
