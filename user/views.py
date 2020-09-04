import json, bcrypt, jwt

from django.views     import View
from django.http      import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.db        import IntegrityError

from .models          import User
from .validation      import ValidationError
from westock.settings import SECRET_KEY, ALGORITHM


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
            return HttpResponse(status = 200)
        
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