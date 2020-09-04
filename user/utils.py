import jwt

from django.http            import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .models                import User
from westock.settings       import SECRET_KEY, ALGORITHM

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization', None)
        try:
            if access_token:
                payload  = jwt.decode(access_token, SECRET_KEY['SECRET_KEY'], ALGORITHM['ALGORITHM'])
                request.account = User.objects.get(id = payload['user_id'])
                return func(self, request, *args, **kwargs)
            return JsonResponse({'MESSAGE':'LOGIN_REQUIRED'}, status = 401)
        
        except User.DoesNotExist:
            return JsonResponse({'MESSAGE':'INVALID_USER'}, status = 401)

        except jwt.DecodeError:
            return JsonResponse({'MESSAGE':'INVALID_TOKEN'}, status = 401)
            
    return wrapper