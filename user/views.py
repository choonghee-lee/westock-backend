import json, bcrypt, jwt, requests

from django.views     import View
from django.http      import HttpResponse, JsonResponse
from django.db.models import Prefetch, Max, Min

from .models          import User, Follow
from product.models   import Product, ProductSize
from sale.models      import Status, Ask, UserAsk, Bid
from .utils           import login_required
from .validation      import ValidationError
from westock.settings import SECRET_KEY, ALGORITHM
from datetime         import datetime

class SignUp(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            if User.objects.filter(email = data['email']).exists():
                return JsonResponse({'MESSAGE':'ALREADY_EXISTS'}, status = 400)
            user = User(
                first_name = data['first_name'],
                last_name  = data['last_name'],
                email      = data['email'],
                password   = data['password']
            )
            user.full_clean()
            user.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
            user.password = user.password.decode('utf-8')
            user.save()
            return JsonResponse({'MESSAGE':'SUCCESS'}, status = 200) 
        
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)

        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status = 400)

        except ValidationError:
            return JsonResponse({'MESSAGE':'INVALID_USER'}, status = 400)

class SignIn(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            if User.objects.filter(email = data['email']).exists():
                user = User.objects.get(email = data['email'])
                if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                    access_token = jwt.encode(
                        {'user_id':user.id}, SECRET_KEY['SECRET_KEY'], ALGORITHM['ALGORITHM']
                    ).decode('utf-8')
                    return JsonResponse({'ACCESS_TOKEN': access_token}, status = 200)
            return JsonResponse({'MESSAGE':"INVALID_USER"}, status = 401)
            
        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        
        except ValueError:
            return JsonResponse({'MESSAGE':'VALUE_ERROR'}, status = 400)

class KakaoSignin(View):
    def post(self, request):
        try:
            access_token = request.headers.get('Authorization')
            user_payload = requests.get(
                'https://kapi.kakao.com/v2/user/me',
                headers = {"Authorization":f"Bearer {access_token}"}
            ).json().get('kakao_account')
            profile = user_payload['profile']
            email   = user_payload['email']
                
            if not User.objects.filter(email = email).exists():
                User.objects.create(first_name = profile.get('nickname'), email = email)

            user         = User.objects.get(email = email)
            access_token = jwt.encode(
                {'user_id':user.id}, SECRET_KEY['SECRET_KEY'], ALGORITHM['ALGORITHM']
            ).decode('utf-8')
            return JsonResponse({'ACCESS_TOKEN':access_token}, status = 200)

        except KeyError:
            return JsonResponse({'MESSAGE':'KEY_ERROR'}, status = 400)
        
class ProductFollow(View):
    @login_required
    def post(self, request):
        data = json.loads(request.body)
        user = request.account

        Follow.objects.filter(user = user).delete()
        product_sizes = ProductSize.objects.filter(product_id = data['product'], size__name__in = data['sizes'])

        for product_size in product_sizes: Follow.objects.create(user = user, product_size = product_size)
        
        return JsonResponse({'MESSAGE':'SUCCESS'}, status = 200)

class SellingList(View):
    @login_required
    def get(self, request):
        user = request.account
        selling_infos = []
        sellings = user.userask_set.all()
        product_sizes = [selling.ask.product_size for selling in sellings]
        for product_size in product_sizes:
            product_image = product_size.product.image_with_product.get(image_type__name = 'list').url
            expired_date = product_size.ask_set.get(userask__user = user).expired_date
            product_info = {
                'product_size_id': product_size.id,
                'product_name':product_size.product.name,
                'product_style':product_size.product.style,
                'image_url': product_image,
                'expired_date': str(expired_date.date()),
                'price': product_size.ask_set.get(userask__user = user).price
            }
            selling_info = product_size.ask_set.all().aggregate(lowest_ask = Min('price'))
            selling_info.update(product_size.bid_set.all().aggregate(highest_bid = Max('price')))
            selling_info.update(product_info)
            selling_infos.append(selling_info)
        
        return JsonResponse({'SELLING_INFOS':selling_infos}, status = 200)
