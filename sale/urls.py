from django.urls import path

from .views import SearchProductForSellView

urlpatterns = [
    path('/sell/search', SearchProductForSellView.as_view()),
]