from django.urls import path

from .views import ProductListView, ProductDetailView, ProductAsksView, ProductBidsView

urlpatterns = [
    path('', ProductListView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
    path('/<int:product_id>/asks', ProductAsksView.as_view()),
    path('/<int:product_id>/bids', ProductBidsView.as_view()),
]
