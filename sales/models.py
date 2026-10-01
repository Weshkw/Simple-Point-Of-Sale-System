from pathlib import PurePosixPath

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction


def copy_image(image, upload_to):
    """Copy a stored image so a record keeps its picture if the original changes.

    Returns the stored name of the copy, or an empty string when the source
    file is missing from storage.
    """
    try:
        with image.storage.open(image.name, "rb") as source:
            content = ContentFile(source.read())
    except FileNotFoundError:
        return ""
    return image.storage.save(f"{upload_to}{PurePosixPath(image.name).name}", content)


class Product(models.Model):
    product_image = models.ImageField(upload_to="product_images/", blank=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_uploaded = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["product_name"]

    def __str__(self):
        return self.product_name


class Sale(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=True, blank=True, related_name="sales"
    )
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_name = models.CharField(max_length=200)
    sale_image = models.ImageField(upload_to="sale_images/", blank=True)
    sale_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-sale_date", "-id"]

    def __str__(self):
        return f"Sale of {self.sale_name} on {self.sale_date}"

    @classmethod
    def record(cls, *, user, product):
        """Record a sale at the product's current catalogue price.

        The name, price and image are copied from the product so the sale
        stays accurate after the product is edited.
        """
        sale = cls(
            user=user,
            product=product,
            sale_name=product.product_name,
            sale_price=product.product_price,
        )
        if product.product_image:
            sale.sale_image.name = copy_image(product.product_image, "sale_images/")
        sale.save()
        return sale

    @transaction.atomic
    def cancel(self, cancellation_reason):
        """Replace this sale with a CancelledSale that records why it was undone."""
        cancelled_sale = CancelledSale.objects.create(
            user=self.user,
            product_name=self.sale_name,
            cancellation_reason=cancellation_reason,
            cancelled_sale_price=self.sale_price,
            cancelled_sale_image=self.sale_image.name,
        )
        self.delete()
        return cancelled_sale


class CancelledSale(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_sales",
    )
    product_name = models.CharField(max_length=200)
    cancellation_reason = models.TextField()
    cancelled_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    cancelled_sale_image = models.ImageField(upload_to="cancelled_sale_images/", blank=True)
    cancelled_sale_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-cancelled_sale_date", "-id"]

    def __str__(self):
        return f"Cancelled sale of {self.product_name} on {self.cancelled_sale_date}"
