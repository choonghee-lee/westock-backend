from django.db.models import Max, Min

from product.models import Image

def get_type_list_image(product):
    images = Image.objects.filter(product=product).select_related('image_type')
    return next((image for image in images if image.image_type.name == 'list'), None)

def make_result_message_json(message):
    return { "message": message }

def make_product_search_result_for_sell_json(product):
    return {
        "id"          : product.pk,
        "name"        : product.name,
        "colorway"    : product.colorway,
        "sub_category": product.category.sub_category.name,
        "image_url"   : get_type_list_image(product).url
    }

def make_product_search_results_for_sell_json(products, count):
    return {
        "count": count,
        "results" :[ 
            make_product_search_result_for_sell_json(product)
            for product in products
        ]
    }

def make_highest_bid_json(product_size):
    return {
        "product_size_id" : product_size.pk,
        "size"            : product_size.size.name,
        "price"           : product_size.bid_set.aggregate(Max('price'))['price__max']
    }

def make_highest_bids_json(product_sizes):
    return [
        make_highest_bid_json(product_size)
        for product_size in product_sizes
    ]

def make_lowest_ask_json(product_size):
    return {
        "product_size_id" : product_size.pk,
        "size"            : product_size.size.name,
        "price"           : product_size.ask_set.aggregate(Min('price'))['price__min']
    }

def make_lowest_asks_json(product_sizes):
    return [
        make_lowest_ask_json(product_size)
        for product_size in product_sizes
    ]

def make_product_detail_for_buy_and_sell_json(product, product_sizes):
    lowest_asks  = make_lowest_asks_json(product_sizes)
    highest_bids = make_highest_bids_json(product_sizes)
    return {
        "id"          : product.pk,
        "name"        : product.name,
        "size_type"   : product.size_type.name,
        "lowest_ask"  : min([ lowest_ask['price']  for lowest_ask in lowest_asks if lowest_ask['price'] != None ]),
        "highest_bid" : max([ highest_bid['price'] for highest_bid in highest_bids if highest_bid['price'] != None ]),
        "lowest_asks" : lowest_asks,
        "highest_bids": highest_bids,
        "image_url"   : get_type_list_image(product).url
    }