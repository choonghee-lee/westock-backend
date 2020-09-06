import json

from django.test import TestCase, Client

from .messages      import MESSAGE_INVALID_SEARCH_TERM
from product.models import (
    Product,
    Specific,
    SizeType,
    ReleaseDate,
    SubCategory,
    MainCategory,
)

class SearchProductForSellViewTest(TestCase):
    def bootstrap_products(self):
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

    def make_search_term_json(self, term):
        return { "search_term": term }

    def request_search_products(self, term, url, content_type):
        client   = Client()
        body     = self.make_search_term_json(term)
        return client.post(url, json.dumps(body), content_type = content_type)

    def setUp(self):
        self.bootstrap_products()

    def tearDown(self):
        Product.objects.all().delete()

    def test_post_search_products_by_term_jordan_success(self):
        response = self.request_search_products('jordan', '/sale/sell/search', 'application/json')
        self.assertEqual(response.status_code, 200)
        
        results  = response.json()['results']
        jordan_1 = results[0]
        jordan_2 = results[1]
        self.assertEqual(jordan_1['name'], 'Jordan 1 Mid Chicago Toe')
        self.assertEqual(jordan_1['colorway'], 'BLACK/GYM RED-WHITE')
        self.assertEqual(jordan_1['sub_category'], 'air jordan')
        self.assertEqual(jordan_2['name'], 'Jordan 2 Retro Just Don Beach')
        self.assertEqual(jordan_2['colorway'], 'BEACH/METALLIC GOLD-UNIVERSITY RED')
        self.assertEqual(jordan_2['sub_category'], 'air jordan')

    def test_post_search_products_by_term_null_fail(self):
        response = self.request_search_products(None, '/sale/sell/search', 'application/json')
        self.assertEqual(response.status_code, 404)
        
        message = response.json()['message']
        self.assertEqual(message, MESSAGE_INVALID_SEARCH_TERM)

    def test_post_search_products_attribute_error_exception(self):
        client   = Client()
        response = client.post('/sale/sell/search', json.dumps(None), content_type =  'application/json')
        self.assertEqual(response.status_code, 400)