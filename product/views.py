import json
import redis

from django.views           import View
from django.http            import JsonResponse
from django.core.cache      import cache
from django.db.models       import Min, Max, Avg
from django.core.exceptions import ObjectDoesNotExist

from collections import Counter
from random      import randint

from .models     import MainCategory, SubCategory, Specific, Product, SizeType, ReleaseDate, Image, ImageType, ProductSize, Size
from sale.models import Ask, UserAsk, Bid, Order

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        tag             = request.GET.get('tag', None)
        productCaterogy = request.GET.get('productCategory', None)
        sizeTypes       = request.GET.get('sizeType', None)
        size            = request.GET.getlist('size', None)
        prices          = request.GET.getlist('prices', None)
        releaseYears    = request.GET.getlist('releaseYear', None)
        sort            = request.GET.get('sort', None)
        page_limit      = int(request.GET.get('limit', 40))
        page_num        = int(request.GET.get('page', 1))

        response_data_set = {'Pagination' : {}, 'Product' : []}

        all_product_list = cache.get('all_product_list')
        if not all_product_list:
            temp_product_list = []
            all_products = Product.objects.select_related('release_date').order_by('id')
            for product in all_products:
                average_price = product.average_price if product.average_price else 0
                volatility = product.volatility if product.volatility else 0.0
                price_premium = product.price_premium if product.price_premium else 0
                temp_product_list.append({
                    'product_id'           : product.id,
                    'name'                 : product.name,
                    'release_date'         : product.release_date.date,
                    'average_price'        : average_price,
                    'price_premium'        : price_premium,
                    'lowest_ask'           : [],
                    'highest_bid'          : [],
                    'sale_count'           : 0
                })

            all_images = Image.objects.filter(image_type = 1).order_by('product')
            for image in all_images:
                temp_product_list[image.product_id - 1]['image'] = image.url

            all_orders = Order.objects.all().select_related('ask', 'bid', 'ask__product_size', 'bid__product_size').order_by('-date')
            for order in all_orders:
                temp_product_list[order.ask.product_size.product_id - 1]['lowest_ask'].append(order.ask.price)
                temp_product_list[order.bid.product_size.product_id - 1]['highest_bid'].append(order.bid.price)
                temp_product_list[order.ask.product_size.product_id - 1]['sale_count'] += 1

            for product in temp_product_list:
                lowest_ask  = int(min(product['lowest_ask'])) if len(product['lowest_ask']) > 0 else 0
                highest_ask = int(max(product['highest_bid'])) if len(product['highest_bid']) > 0 else 0
                last_sale   = int(product['lowest_ask'][0]) if len(product['lowest_ask']) > 0 else 0
                product['lowest_ask']        = lowest_ask
                product['highest_bid']       = highest_ask
                product['product_ask_price'] = lowest_ask
                product['most_popular']      = product['sale_count']
                product['last_sales']        = last_sale

            cache.set('all_product_list', temp_product_list)
            all_product_list = temp_product_list

        if sort == 'most_popular':
            all_product_list = sorted(all_product_list, reverse = True, key = lambda x : x['sale_count'])
        elif sort == 'lowest_ask':
            all_product_list = sorted(all_product_list, key = lambda x : x['lowest_ask'])
        elif sort == 'highest_bid':
            all_product_list = sorted(all_product_list, reverse = True, key = lambda x : x['highest_bid'])
        elif sort == 'release_date':
            all_product_list = sorted(all_product_list, reverse = True, key = lambda x : x['release_date'])
        elif sort == 'last_sales':
            all_product_list = sorted(all_product_list, reverse = True, key = lambda x : x['last_sales'])
        elif sort == 'average_price':
            all_product_list = sorted(all_product_list, reverse = True, key = lambda x : x['average_price'])
        elif sort == 'price_premium':
            all_product_list = sorted(all_product_list, reverse = True, key = lambda x : x['price_premium'])

        count = 0
        start_index = (page_num * page_limit) - page_limit
        end_index = page_num * page_limit
        for product in all_product_list[start_index:end_index]:
            response_data_set['Product'].append(product)
            count += 1
            if count == page_limit:
                break;

        product_total        = len(all_product_list)
        page_count_condition = product_total % page_limit
        page_count           = int(product_total // page_limit) if page_count_condition == 0 else int(product_total // page_limit) + 1
        response_data_set['Pagination']['limit']         = page_limit
        response_data_set['Pagination']['page']          = page_num
        response_data_set['Pagination']['product_total'] = product_total
        response_data_set['Pagination']['last_page']     = page_count
        response_data_set['Pagination']['current_page']  = page_num
        response_data_set['Pagination']['next_page']     = page_num + 1 if not(page_num == page_count) else None
        response_data_set['Pagination']['previous_page'] = page_num - 1 if not(page_num == 1) else None

        return JsonResponse({'message' : response_data_set}, status = 200)

class ProductDetailView(View):
    def get(self, request, product_id):
        product       = Product.objects.get(id = product_id)

        detail_images = Image.objects.filter(product = product_id, image_type = 2).get().url
        week_52_high, week_52_low = 0, 100000
        size_info_list = []
        size_list      = []

        productsize_list = ProductSize.objects.filter(product = product_id)
        for productsize in productsize_list:
            size_list.append(productsize.id)
            target_orders = Order.objects.filter(ask__product_size_id = productsize.id).select_related('bid', 'ask').order_by('date')
            if len(target_orders) > 1:
                recent_price, before_price, recent_date = target_orders[0].ask.price, target_orders[1].ask.price, target_orders[0].date
            elif len(target_orders) == 1:
                recent_price, before_price, recent_date = target_orders[0].ask.price, 0, target_orders[0].date
            else:
                recent_price, before_price, recent_date = 0, 0, None

            difference = int(recent_price - before_price)
            percentage = 0 if difference == 0 else int((difference / recent_price) * 100)

            lowAsk  = Ask.objects.filter(product_size_id = productsize.id).aggregate(Min('price'))['price__min']
            highBid = Bid.objects.filter(product_size_id = productsize.id).aggregate(Max('price'))['price__max']
            if lowAsk  != None and week_52_low > lowAsk: week_52_low = int(lowAsk)
            if highBid != None and week_52_high < highBid: week_52_high = int(highBid)

            size_info_list.append({
                'size'       : productsize.size.name,
                'lowestAsk'  : '$' + str(int(lowAsk)) if lowAsk else '$' + str(randint(50, 500)),
                'highestBid' : '$' + str(int(highBid)) if highBid else '$' + str(randint(50, 500)),
                'lastSale'   : '$' + str(int(recent_price)),
                'lastSize'   : None,
                'difference' : '-$' + str(difference)[1 : ] if difference < 0 else '+$' + str(difference) if difference > 0 else str(difference),
                'percentage' : str(percentage) + '%' if percentage < 0 else '+' + str(percentage) + '%' if percentage > 0 else str(percentage) + '%',
                'lastDate'   : recent_date
            })

        temp_lastDate = 0
        size_all = {'size' : 'All', 'lowestAsk' : '$100000', 'highestBid' : '$0', 'lastSale' : 0,
                    'lastSize' : '', 'difference' : 0, 'percentage' : 0, 'lastDate' : None}

        for item in size_info_list:
            if not(item['highestBid'] == None) and int(size_all['highestBid'][1:]) < int(item['highestBid'][1:]):
                size_all['highestBid'] = item['highestBid']
            if not(item['lowestAsk'] == None) and int(size_all['lowestAsk'][1:]) > int(item['lowestAsk'][1:]):
                size_all['lowestAsk'] = item['lowestAsk']

            if item['lastDate'] == None:
                continue
            else:
                if temp_lastDate == 0:
                    temp_lastDate = item['lastDate']
                if temp_lastDate <= item['lastDate']:
                    temp_lastDate          = item['lastDate']
                    size_all['size']       = 'All'
                    size_all['lastSale']   = item['lastSale']
                    size_all['lastSize']   = item['size']
                    size_all['difference'] = item['difference']
                    size_all['percentage'] = item['percentage']

        size_info_list.insert(0, size_all)

        related_product_list = []
        related_range        = range(product_id + 1, product_id + 16) if product_id < 1560 else range(product_id - 1, product_id - 16, -1)
        for index in related_range:
            related_item = Product.objects.get(id = index)
            temp_price = related_item.average_price if related_item.average_price else randint(50, 1000)
            related_product_list.append({
                    'product_id'    : index,
                    'name'          : related_item.name,
                    'thumnail'      : Image.objects.filter(product = index, image_type = 1).get().url,
                    'average_price' : '$' + str(temp_price)
            })

        all_sale_list = []
        target_asks   = Ask.objects.filter(product_size_id__in = size_list).prefetch_related('order_set').order_by('order__date')

        for ask in target_asks:
            full_date = str(ask.order_set.get().date).split(' ')
            all_sale_list.append({
                'size'       : ProductSize.objects.get(id = ask.product_size_id).size.name,
                'sale_price' : int(ask.price),
                'date'       : full_date[0],
                'time'       : full_date[1]
            })

        average_price   = int(product.average_price) if product.average_price != None else 0
        volatility      = product.volatility * 100 if product.volatility      != None else 0
        trade_range_val = int(average_price * (volatility / 100))

        detail_data_set = {
            'product_id'       : product.id,
            'name'             : product.name,
            'ticker'           : product.ticker,
            'series'           : product.category.name,
            'sub_category'     : product.category.sub_category.name,
            'main_category'    : product.category.sub_category.main_category.name,
            'description'      : product.description,
            'style'            : product.style,
            'colorway'         : product.colorway,
            'retail_price'     : int(product.retail_price),
            'release_date'     : product.release_date.date,
            '#_of_sales'       : randint(500, 4000),
            'average_price'    : '$' + str(average_price),
            'price_premium'    : str(product.price_premium / 10) + '%' if product.price_premium != None else '0%',
            'detail_images'    : detail_images,
            '52week_high'      : '$' + str(week_52_high),
            '52week_low'       : '$' + str(week_52_low),
            'trade_range'      : '$' + str(average_price - trade_range_val) + ' - ' + '$' + str(average_price + trade_range_val),
            'volatility'       : str(volatility) + '%',
            'size_info_list'   : size_info_list,
            'related_products' : related_product_list,
            'all_sale_list'    : all_sale_list
        }

        return JsonResponse({'message' : detail_data_set}, status = 200)

class ProductAsksView(View):
    def get(self, request, product_id):
        input_size = request.GET.get('size', None)

        ask_data_set = []
        if input_size:
            size_id             = ProductSize.objects.filter(product_id = product_id, size__name = input_size).get().id
            target_productsizes = ProductSize.objects.filter(product_id = product_id, size_id = size_id).prefetch_related('ask_set')
            for productsize in target_productsizes:
                try:
                    ask_data_set.append({
                        'size'  : input_size,
                        'price' : productsize.ask_set.values('price').get()['price'],
                        'count' : Ask.objects.filter(product_size_id = productsize.id, price = productsize.ask_set.values('price').get()['price']).count()
                    })
                except ObjectDoesNotExist:
                    return JsonResponse({'message':'EMPTY'}, status = 200)
        if not(input_size):
            product_size_list   = []
            target_productsizes = ProductSize.objects.filter(product_id = product_id)
            for productsize in target_productsizes:
                product_size_list.append(productsize.id)

            target_asks = Ask.objects.filter(product_size_id__in=product_size_list).select_related('product_size')
            for ask in target_asks:
                ask_data_set.append({
                    'size'  : ask.product_size.size.name,
                    'price' : ask.price,
                    'count' : 1
                })
            ask_data_set = sorted(ask_data_set, reverse = True, key = lambda x : x['price'])
        return JsonResponse({'message':ask_data_set}, status = 200)

class ProductBidsView(View):
    def get(self, request, product_id):
        input_size = request.GET.get('size', None)

        bid_data_set = []
        if input_size:
            size_id             = ProductSize.objects.filter(product_id = product_id, size__name = input_size).get().id
            target_productsizes = ProductSize.objects.filter(product_id = product_id, size_id = size_id).prefetch_related('bid_set')
            for productsize in target_productsizes:
                try:
                    bid_data_set.append({
                        'size'  : input_size,
                        'price' : productsize.bid_set.values('price').get()['price'],
                        'count' : Bid.objects.filter(product_size_id = productsize.id, price = productsize.bid_set.values('price').get()['price']).count()
                    })
                except ObjectDoesNotExist:
                    return JsonResponse({'message':'EMPTY'}, status = 200)

        if not(input_size):
            product_size_list   = []
            target_productsizes = ProductSize.objects.filter(product_id = product_id)
            for productsize in target_productsizes:
                product_size_list.append(productsize.id)

            target_bids = Bid.objects.filter(product_size_id__in=product_size_list).select_related('product_size')
            for bid in target_bids:
                bid_data_set.append({
                    'size'  : bid.product_size.size.name,
                    'price' : bid.price,
                    'count' : 1
                })
            bid_data_set = sorted(bid_data_set, reverse = True, key = lambda x : x['price'])
        return JsonResponse({'message':bid_data_set}, status = 200)
