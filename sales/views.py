from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CancelSaleForm
from .models import Product, Sale


@login_required
def home(request):
    return render(request, "sales/home.html", {"products": Product.objects.all()})


@login_required
def sales_record(request):
    return render(request, "sales/sales_record.html", {"sales": request.user.sales.all()})


@login_required
@require_POST
def cancel_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk, user=request.user)
    form = CancelSaleForm(request.POST)
    if form.is_valid():
        sale.cancel(form.cleaned_data["cancellation_reason"])
        messages.success(request, f"Sale of {sale.sale_name} has been cancelled.")
    else:
        messages.error(request, "Give a reason to cancel a sale.")
    return redirect("sales-record")


@login_required
def cancelled_sales(request):
    return render(
        request,
        "sales/cancelled_sales.html",
        {"cancelled_sales": request.user.cancelled_sales.all()},
    )
