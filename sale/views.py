import json
from json.decoder import JSONDecodeError

from django.views import View
from django.http  import JsonResponse

from .messages      import (
    MESSAGE_INVALID_JSON_FORMAT,
    MESSAGE_INVALID_SEARCH_TERM,
)
from .make_jsons    import (
    make_result_message_json,
    make_product_search_results_for_sell_json
)
from product.models import (
    Product
)

class SearchProductForSellView(View):
    def post(self, request):
        DEFAULT_LIMIT = 5
        try:
            data        = json.loads(request.body)
            search_term = data.get('search_term', None)
            if not search_term:
                body = make_result_message_json(MESSAGE_INVALID_SEARCH_TERM)
                return JsonResponse(body, status = 404)
                
            products = Product.objects.filter(name__icontains = search_term)\
                        .select_related('category__sub_category')[:DEFAULT_LIMIT]
            body     = make_product_search_results_for_sell_json(products)
            return JsonResponse(body, status = 200)
        except (JSONDecodeError, AttributeError):
            body = make_result_message_json(MESSAGE_INVALID_JSON_FORMAT)
            return JsonResponse(body, status = 400)