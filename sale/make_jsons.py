def make_result_message_json(message):
    return { "message": message }

def make_product_search_result_for_sell_json(product):
    return {
        "id"          : product.pk,
        "name"        : product.name,
        "colorway"    : product.colorway,
        "sub_category": product.category.sub_category.name
    }

def make_product_search_results_for_sell_json(products):
    return {
        "results" :[ 
            make_product_search_result_for_sell_json(product)
            for product in products
        ]
    }