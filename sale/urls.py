from django.urls import path

from .views import (
    SearchProductForSellView,
    ProductDetailForBuyAndSellView,
)

urlpatterns = [
    path('/search', SearchProductForSellView.as_view()),
    path('/product', ProductDetailForBuyAndSellView.as_view())
]