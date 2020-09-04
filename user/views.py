import json, bcrypt, jwt, requests

from django.views     import View
from django.http      import HttpResponse, JsonResponse
from django.db.models import Prefetch

from .models          import User, Follow
from product.models   import Product, ProductSize
from .utils           import login_required
from .validation      import ValidationError
from westock.settings import SECRET_KEY, ALGORITHM, SOCIAL_KEY

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
                User.objects.create(
                    first_name = profile.get('nickname'),
                    email      = email
                )

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