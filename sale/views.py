import json
from json.decoder import JSONDecodeError

from django.views import View
from django.http  import JsonResponse

from .messages      import (
    MESSAGE_INVALID_JSON_FORMAT,
    MESSAGE_INVALID_SEARCH_TERM,
    MESSAGE_INVALID_PRODUCT_ID,
    MESSAGE_KEY_ERROR
)
from .make_jsons    import (
    make_result_message_json,
    make_product_search_results_for_sell_json,
    make_product_detail_for_buy_and_sell_json,
)
from product.models import (
    Product,
    ProductSize,
)

class SearchProductForSellView(View):
    def post(self, request):
        DEFAULT_LIMIT = 20
        try:
            data        = json.loads(request.body)
            search_term = data['search_term']
            if not search_term:
                body = make_result_message_json(MESSAGE_INVALID_SEARCH_TERM)
                return JsonResponse(body, status = 400)
                
            total_count = Product.objects.filter(name__icontains = search_term).count()
            products    = Product.objects.filter(name__icontains = search_term)\
                        .select_related('category__sub_category')[:DEFAULT_LIMIT]
            body        = make_product_search_results_for_sell_json(products, total_count)
            return JsonResponse(body, status = 200)
        except KeyError:
            body = make_result_message_json(MESSAGE_KEY_ERROR)
            return JsonResponse(body, status = 400)
        except (JSONDecodeError, AttributeError):
            body = make_result_message_json(MESSAGE_INVALID_JSON_FORMAT)
            return JsonResponse(body, status = 400)

class ProductDetailForBuyAndSellView(View):
    def post(self, request):
        try:
            data       = json.loads(request.body)
            product_id = data['product_id']
            if not product_id or\
               product_id.isalpha() or\
               not Product.objects.filter(pk = product_id).exists():
                body = make_result_message_json(MESSAGE_INVALID_PRODUCT_ID)
                return JsonResponse(body, status = 400)

            product       = Product.objects.filter(pk = product_id)\
                            .prefetch_related('productsize_set').get()
            product_sizes = product.productsize_set.select_related('size')\
                            .prefetch_related('ask_set', 'bid_set')
            body          = make_product_detail_for_buy_and_sell_json(product, product_sizes)
            return JsonResponse(body, status = 200)
        except KeyError:
            body = make_result_message_json(MESSAGE_KEY_ERROR)
            return JsonResponse(body, status = 400)
        except (JSONDecodeError, AttributeError):
            body = make_result_message_json(MESSAGE_INVALID_JSON_FORMAT)
            return JsonResponse(body, status = 400)