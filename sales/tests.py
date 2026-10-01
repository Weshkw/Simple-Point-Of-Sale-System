import shutil
import tempfile
from decimal import Decimal

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from .consumers import SalesConsumer
from .models import CancelledSale, Product, Sale

MEDIA_ROOT = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SaleModelTests(TestCase):
    def setUp(self):
        self.cashier = get_user_model().objects.create_user("cashier", password="pw")
        self.product = Product.objects.create(
            product_name="Soda",
            product_price=Decimal("60.00"),
            product_image=SimpleUploadedFile("soda.gif", b"GIF89a", content_type="image/gif"),
        )

    def test_record_copies_catalogue_details(self):
        sale = Sale.record(user=self.cashier, product=self.product)

        self.assertEqual(sale.sale_name, "Soda")
        self.assertEqual(sale.sale_price, Decimal("60.00"))
        self.assertTrue(sale.sale_image.name.startswith("sale_images/"))
        self.assertTrue(sale.sale_image.storage.exists(sale.sale_image.name))

    def test_record_survives_a_missing_product_image(self):
        self.product.product_image.storage.delete(self.product.product_image.name)

        sale = Sale.record(user=self.cashier, product=self.product)

        self.assertEqual(sale.sale_image.name, "")

    def test_cancel_moves_the_sale_to_cancelled_sales(self):
        sale = Sale.record(user=self.cashier, product=self.product)

        cancelled = sale.cancel("Customer changed their mind")

        self.assertFalse(Sale.objects.exists())
        self.assertEqual(cancelled.product_name, "Soda")
        self.assertEqual(cancelled.cancelled_sale_price, Decimal("60.00"))
        self.assertEqual(cancelled.cancellation_reason, "Customer changed their mind")
        self.assertEqual(cancelled.cancelled_sale_image.name, sale.sale_image.name)


class SalesViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.cashier = user_model.objects.create_user("cashier", password="pw")
        self.other_cashier = user_model.objects.create_user("other", password="pw")
        self.product = Product.objects.create(product_name="Bread", product_price=Decimal("55"))
        self.sale = Sale.record(user=self.cashier, product=self.product)
        self.cancel_url = reverse("cancel-sale", args=[self.sale.pk])

    def test_every_page_requires_login(self):
        for name in ["home", "sales-record", "cancelled-sales"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(response, f"{reverse('login')}?next={reverse(name)}")

    def test_sales_record_lists_only_the_cashiers_own_sales(self):
        Sale.record(user=self.other_cashier, product=self.product)
        self.client.force_login(self.cashier)

        response = self.client.get(reverse("sales-record"))

        self.assertEqual(list(response.context["sales"]), [self.sale])

    def test_cancel_with_reason_records_the_cancellation(self):
        self.client.force_login(self.cashier)

        response = self.client.post(self.cancel_url, {"cancellation_reason": "Wrong item"})

        self.assertRedirects(response, reverse("sales-record"))
        self.assertFalse(Sale.objects.filter(pk=self.sale.pk).exists())
        self.assertEqual(CancelledSale.objects.get().cancellation_reason, "Wrong item")
        self.assertContains(self.client.get(reverse("cancelled-sales")), "Wrong item")

    def test_cancel_without_reason_keeps_the_sale(self):
        self.client.force_login(self.cashier)

        self.client.post(self.cancel_url, {"cancellation_reason": "  "})

        self.assertTrue(Sale.objects.filter(pk=self.sale.pk).exists())
        self.assertFalse(CancelledSale.objects.exists())

    def test_cashier_cannot_cancel_someone_elses_sale(self):
        self.client.force_login(self.other_cashier)

        response = self.client.post(self.cancel_url, {"cancellation_reason": "Not mine"})

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Sale.objects.filter(pk=self.sale.pk).exists())

    def test_cancel_rejects_get(self):
        self.client.force_login(self.cashier)

        self.assertEqual(self.client.get(self.cancel_url).status_code, 405)


class SalesConsumerTests(TransactionTestCase):
    def setUp(self):
        self.cashier = get_user_model().objects.create_user("cashier", password="pw")
        self.product = Product.objects.create(product_name="Milk", product_price=Decimal("65"))

    def communicator_for(self, user):
        communicator = WebsocketCommunicator(SalesConsumer.as_asgi(), "/ws/sales/")
        communicator.scope["user"] = user
        return communicator

    async def test_anonymous_connections_are_refused(self):
        connected, _ = await self.communicator_for(AnonymousUser()).connect()

        self.assertFalse(connected)

    async def test_sale_uses_the_catalogue_price_not_the_clients(self):
        communicator = self.communicator_for(self.cashier)
        await communicator.connect()

        await communicator.send_json_to({"product_id": self.product.pk, "product_price": "1"})
        response = await communicator.receive_json_from()
        await communicator.disconnect()

        self.assertEqual(
            response,
            {"type": "sale_recorded", "sale": {"product_name": "Milk", "sale_price": "65.00"}},
        )
        sale = await Sale.objects.aget()
        self.assertEqual(sale.sale_price, Decimal("65.00"))
        self.assertEqual(sale.user_id, self.cashier.pk)

    async def test_unknown_product_is_reported_as_a_failed_sale(self):
        communicator = self.communicator_for(self.cashier)
        await communicator.connect()

        await communicator.send_json_to({"product_id": "not-a-product"})
        response = await communicator.receive_json_from()
        await communicator.disconnect()

        self.assertEqual(response, {"type": "sale_failed"})
        self.assertFalse(await Sale.objects.aexists())
