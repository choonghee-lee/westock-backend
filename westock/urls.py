from django.urls import path, include

urlpatterns = [
    path('users', include('user.urls')),
    path('sale', include('sale.urls')),
    path('products', include('product.urls')),
]
