from django.urls import path
from . import views

urlpatterns =[
   path('', views.home, name='home'), 
   path('login/',views.login_view, name='login'),
   path('logout/', views.logout_view, name='logout'),
   path('sales/',views.usersalesrecords, name='salesrecord'),
   path('cancel_sale/<int:pk>/', views.cancel_sale, name='cancel-sale'), 
   path('cancelled_sales/',views.cancelledSales, name='cancelled-sales'),
   
]