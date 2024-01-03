
from .models import Product,Sale,CancelledSale
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages


# Create your views here.
@login_required(login_url='login')
def home(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request,'instantbusinessressponse/home.html', context)


@login_required(login_url='login')
def usersalesrecords(request):
    # Filter sales records for the current user
    Sales = Sale.objects.filter(user=request.user)
    context = {'Sales': Sales}
    return render(request, 'instantbusinessressponse/userSalesRecord.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Use Django's login function to log the user in.
            login(request, user)
            return redirect('home')
        else:
            return redirect('login')
        
    return render(request, 'instantbusinessressponse/login.html')

def logout_view(request):
    # Use Django's logout function to log the user out
    logout(request)
    
    # Redirect to the desired page after logout, such as the login page
    return redirect('login')


@login_required(login_url='login')
def cancel_sale(request, pk):
    sale_instance = get_object_or_404(Sale, pk=pk, user=request.user)

    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason')

        # Ensure that sale_instance has a product associated with it
        if sale_instance.product:
            product_name = sale_instance.product.product_name

            # Call the cancel_sale method to move details to CancelledSale and delete the sale
            cancelled_sale_instance = sale_instance.cancel_sale(cancellation_reason)

            # Add success message with the product name
            success_message = f'Sale of {product_name} has been successfully canceled.'
            messages.success(request, success_message)

            # Perform any additional actions or redirect the user as needed
            return redirect('salesrecord')
        else:
            # Handle the case where the sale_instance has no associated product
            messages.error(request, 'Unable to cancel sale. Product information not available.')

    # Render the cancel_sale template with the sale instance
    return render(request, 'instantbusinessressponse/userSalesRecord.html', {'sale_instance': sale_instance})



def cancelledSales(request):
    cancelledsales=CancelledSale.objects.filter(user=request.user)
    context = {'cancelledsales':cancelledsales}
    return render(request, 'instantbusinessressponse/canceled_sales.html', context)



