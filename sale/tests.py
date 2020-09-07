import json

from django.test import TestCase, Client

from .messages      import (
    MESSAGE_INVALID_SEARCH_TERM,
    MESSAGE_INVALID_PRODUCT_ID,
)
from product.models import (
    Size,
    Product,
    Specific,
    SizeType,
    ReleaseDate,
    SubCategory,
    MainCategory,
    ProductSize,
    Image,
    ImageType,
)
from sale.models   import(
    Ask,
    Bid,
    Status,
    UserAsk,
)
from user.models   import User
from .utils        import convert_str_to_datetime

def bootstrap_products():
    main_category = MainCategory.objects.create(
        pk   = 1,
        name = 'sneakers',
    )
    sub_category = SubCategory.objects.create(
        pk            = 1,
        name          = 'air jordan',
        main_category = main_category,
    )
    size_type_men = SizeType.objects.create(
        pk   = 1,
        name = 'men',
    )
    image_type = ImageType.objects.create(name = "list")

    release_date_1 = ReleaseDate.objects.create(
        pk   = 1,
        date = "2020-04-01",
    )
    specific_1 = Specific.objects.create(
        pk           = 1,
        name         = "1",
        sub_category = sub_category
    )
    jordan_1 = Product.objects.create(
        pk           = 1,
        name         = "Jordan 1 Mid Chicago Toe",
        ticker       = "AJ1M-CHIT",
        style        = "554724-069",
        colorway     = "BLACK/GYM RED-WHITE",
        retail_price = 115,
        release_date = release_date_1,
        size_type    = size_type_men,
        category     = specific_1,
    )
    Image.objects.create(
        product    = jordan_1,
        image_type = image_type,
        url        = "https://stockx.imgix.net/Air-Jordan-1-Mid-Chicago-Toe-Product.jpg?fit=fill&bg=FFFFFF&w=300&h=214&auto=format,compress&trim=color&q=90&dpr=2&updated_at=1596134467"
    )

    release_date_2 = ReleaseDate.objects.create(
        pk   = 2,
        date = "2016-01-30",
    )
    specific_2 = Specific.objects.create(
        pk           = 2,
        name         = "2",
        sub_category = sub_category
    )
    jordan_2 = Product.objects.create(
        pk           = 2,
        name         = "Jordan 2 Retro Just Don Beach",
        ticker       = "AJ2-JSTDONBCH",
        style        = "834825-250",
        colorway     = "BEACH/METALLIC GOLD-UNIVERSITY RED",
        retail_price = 650,
        release_date = release_date_2,
        size_type    = size_type_men,
        category     = specific_2,
    )
    Image.objects.create(
        product    = jordan_2,
        image_type = image_type,
        url        = "https://stockx.imgix.net/Air-Jordan-2-Retro-Just-Don-Beach-Product.jpg?fit=fill&bg=FFFFFF&w=300&h=214&auto=format,compress&trim=color&q=90&dpr=2&updated_at=1538080256"
    )

    return [ jordan_1, jordan_2 ]
    
def bootstrap_sizes():
    size_1 = Size.objects.create(name = "6")
    size_2 = Size.objects.create(name = "8.5")
    return [ size_1, size_2 ]
    
def bootstrap_product_sizes(products, sizes):
    return [
        ProductSize.objects.create(product=product, size=size)
        for product in products
        for size in sizes
    ]

def bootstrap_user():
    return User.objects.create(
        pk         = 1,
        first_name = "Brandon",
        last_name  = "Bale",
        email      = "brandon@westock.com",
        password   = "Helloworld!",
    )

def bootstrap_asks(product_sizes, status, user):
    for product_size in product_sizes:
        ask = Ask.objects.create(
            price        = 200,
            expired_date = convert_str_to_datetime('2020-09-01'),
            status       = status,
            product_size = product_size,
            created_at   = convert_str_to_datetime('2020-08-10'),
        )
        UserAsk.objects.create(
            ask  = ask,
            user = user
        )

def bootstrap_bids(product_sizes, status, user):
    for product_size in product_sizes:
        Bid.objects.create(
            user         = user,
            price        = 300,
            expired_date = convert_str_to_datetime('2020-09-01'),
            status       = status,
            product_size = product_size,
            created_at   = convert_str_to_datetime('2020-08-10'),
        )

def bootstrap_image_type(name):
    return ImageType.objects.create(name=name)

def bootstrap_images(product, image_type, urls):
    Image.objects.create(
        product    = product,
        image_type = image_type,
        url        = url
    )

def delete_product():
    MainCategory.objects.all().delete()
    SubCategory.objects.all().delete()
    SizeType.objects.all().delete()
    ImageType.objects.all().delete()
    ReleaseDate.objects.all().delete()
    Specific.objects.all().delete()
    ImageType.objects.all().delete()
    Product.objects.all().delete()

class SearchProductForSellViewTest(TestCase):
    def make_search_term_json(self, term):
        return { "search_term": term }

    def request_search_products(self, term, url, content_type):
        client   = Client()
        body     = self.make_search_term_json(term)
        return client.post(url, json.dumps(body), content_type = content_type)

    def setUp(self):
        bootstrap_products()

    def tearDown(self):
        delete_product()

    def test_post_search_products_by_term_jordan_success(self):
        response = self.request_search_products('jordan', '/sale/search', 'application/json')
        self.assertEqual(response.status_code, 200)
        
        results  = response.json()['results']
        jordan_1 = results[0]
        jordan_2 = results[1]
        self.assertEqual(jordan_1['name'], 'Jordan 1 Mid Chicago Toe')
        self.assertEqual(jordan_1['colorway'], 'BLACK/GYM RED-WHITE')
        self.assertEqual(jordan_1['sub_category'], 'air jordan')
        self.assertEqual(jordan_1['image_url'], 'https://stockx.imgix.net/Air-Jordan-1-Mid-Chicago-Toe-Product.jpg?fit=fill&bg=FFFFFF&w=300&h=214&auto=format,compress&trim=color&q=90&dpr=2&updated_at=1596134467')
        self.assertEqual(jordan_2['name'], 'Jordan 2 Retro Just Don Beach')
        self.assertEqual(jordan_2['colorway'], 'BEACH/METALLIC GOLD-UNIVERSITY RED')
        self.assertEqual(jordan_2['sub_category'], 'air jordan')
        self.assertEqual(jordan_2['image_url'], 'https://stockx.imgix.net/Air-Jordan-2-Retro-Just-Don-Beach-Product.jpg?fit=fill&bg=FFFFFF&w=300&h=214&auto=format,compress&trim=color&q=90&dpr=2&updated_at=1538080256')

    def test_post_search_products_by_term_null_fail(self):
        response = self.request_search_products(None, '/sale/search', 'application/json')
        self.assertEqual(response.status_code, 404)
        
        message = response.json()['message']
        self.assertEqual(message, MESSAGE_INVALID_SEARCH_TERM)

    def test_post_search_products_attribute_error_exception(self):
        client   = Client()
        response = client.post('/sale/search', json.dumps(None), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)

class ProductDetailForBuyAndSellViewTest(TestCase):
    def make_product_id_json(self, pk):
        return { 'product_id': pk }

    def setUp(self):
        products      = bootstrap_products()
        sizes         = bootstrap_sizes()
        product_sizes = bootstrap_product_sizes(products, sizes)
        status        = Status.objects.create(name = 'current')
        user          = bootstrap_user()
        image_type    = bootstrap_image_type('list')
        bootstrap_images
        bootstrap_asks(product_sizes, status, user)
        bootstrap_bids(product_sizes, status, user)

    def tearDown(self):
        delete_product()
        User.objects.all().delete()
        Size.objects.all().delete()
        Status.objects.all().delete()
        ProductSize.objects.all().delete()

    def test_post_product_detail_to_buy_or_sell_id_1_success(self):
        client   = Client()
        body     = self.make_product_id_json("1")
        response = client.post('/sale/product', json.dumps(body), content_type = 'application/json')
        self.assertEqual(response.status_code, 200)

        result       = response.json()
        lowest_asks  = result['lowest_asks']
        highest_bids = result['highest_bids']
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'Jordan 1 Mid Chicago Toe')
        self.assertEqual(result['size_type'], 'men')
        self.assertEqual(result['lowest_ask'],'200.0000')
        self.assertEqual(result['highest_bid'], '300.0000')
        self.assertEqual(result['image_url'], 'https://stockx.imgix.net/Air-Jordan-1-Mid-Chicago-Toe-Product.jpg?fit=fill&bg=FFFFFF&w=300&h=214&auto=format,compress&trim=color&q=90&dpr=2&updated_at=1596134467')
        self.assertEqual(lowest_asks[0]['size'], '6')
        self.assertEqual(lowest_asks[0]['price'], '200.0000')
        self.assertEqual(lowest_asks[0]['product_size_id'], 5)
        self.assertEqual(highest_bids[0]['size'], '6')
        self.assertEqual(highest_bids[0]['price'], '300.0000')
        self.assertEqual(highest_bids[0]['product_size_id'], 5)

    def test_post_product_detail_to_buy_or_sell_id_weird_string_fail(self):
        client   = Client()
        body     = self.make_product_id_json("null")
        response = client.post('/sale/product', json.dumps(body), content_type = 'application/json')
        self.assertEqual(response.status_code, 404)

        result = response.json()
        self.assertEqual(result['message'], MESSAGE_INVALID_PRODUCT_ID)

    def test_post_product_detail_to_buy_or_sell_attribute_error_exception(self):
        client   = Client()
        response = client.post('/sale/product', json.dumps(None), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)