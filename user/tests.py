import json, bcrypt, jwt

from django.test      import TestCase, Client

from unittest.mock    import Mock, MagicMock, patch
from .models          import User
from westock.settings import SECRET_KEY, ALGORITHM
from .utils           import login_required

class UserSignUpTest(TestCase):
    def setUp(self):
        User.objects.create(
            first_name = 'origin_first',
            last_name  = 'origin_last',
            email      = 'origin@gmail.com',
            password   = 'Test4321!'
        )
    
    def tearDown(self):
        User.objects.all().delete()
    
    def test_user_sign_up_post_success(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmail.com",
            "password":   "Test4321!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_user_sign_up_post_duplicated_email(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "origin@gmail.com",
            "password":   "Test4321!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'ALREADY_EXISTS'})

    def test_user_sign_up_post_key_error(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmail.com"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'KEY_ERROR'})

    def test_user_sign_up_post_email_at_validatoin(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "testgmail.com",
            "password":   "Test4321!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'INVALID_USER'})
    
    def test_user_sign_up_post_email_dot_validation(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmailcom",
            "password":   "Test4321!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'INVALID_USER'})

    def test_user_sign_up_post_password_length_validation(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmailcom",
            "password":   "Test432!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'INVALID_USER'})

    def test_user_sign_up_post_password_special_character_validation(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmailcom",
            "password":   "Test43210"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'INVALID_USER'})

    def test_user_sign_up_post_password_upper_word_validation(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmailcom",
            "password":   "test4321!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'INVALID_USER'})

    def test_user_sign_up_post_password_number_validation(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmailcom",
            "password":   "TestTest!"
        }

        response = client.post('/users/sign-up', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE': 'INVALID_USER'})

    def test_user_sign_up_post_page_not_found(self):
        client = Client()
        user = {
            "first_name": "test_first",
            "last_name":  "test_last",
            "email":      "test@gmail.com",
            "password":   "Test4321!"
        }

        response = client.post('/users/signup', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 404)

class UserSignInTest(TestCase):
    def setUp(self):
        user = User(
            first_name = 'origin_first',
            last_name  = 'origin_last',
            email      = 'origin@gmail.com',
            password   = 'Test4321!'
        )
        user.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        user.password = user.password.decode('utf-8')
        user.save()
    
    def tearDown(self):
        User.objects.all().delete()

    def test_user_sign_in_post_success(self):
        client = Client()
        user = {
            "email":    "origin@gmail.com",
            "password": "Test4321!"
        }

        response = client.post('/users/sign-in', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_user_sign_in_post_account_invalid(self):
        client = Client()
        user = {
            "email":    "test@gmail.com",
            "password": "Test4321!"
        }

        response = client.post('/users/sign-in', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"MESSAGE": "INVALID_USER"})
    
    def test_user_sign_in_post_password_invalid(self):
        client = Client()
        user = {
            "email":    "origin@gmail.com",
            "password": "Test4321@"
        }

        response = client.post('/users/sign-in', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"MESSAGE": "INVALID_USER"})

    def test_user_sign_in_post_key_error(self):
        client = Client()
        user = {
            "account":  "origin@gmail.com",
            "password": "Test4321!"
        }

        response = client.post('/users/sign-in', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"MESSAGE": "KEY_ERROR"})

    def test_user_sign_in_page_not_found(self):
        client = Client()
        user = {
            "email":    "origin@gmail.com",
            "password": "Test4321!"
        }

        response = client.post('/users/signin', json.dumps(user), content_type = 'application/json')
        self.assertEqual(response.status_code, 404)
    
class KakaoSignInTest(TestCase):
    def setUp(self):
        User.objects.create(
            first_name = 'origin_first',
            last_name  = 'origin_last',
            email      = 'origin@gmail.com',
            password   = 'Test4321!'
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch('user.views.requests')
    def test_kakao_sign_in_success(self, mocked_request):
        class Fakeresponse:
            def json(self):
                return {
                    'kakao_account': {
                          'profile': {'nickname':'test'},
                            'email': 'test@gmail.com'
                    }
                }
        client             = Client()
        mocked_request.get = MagicMock(return_value = Fakeresponse())
        headers            = {'Authorization':'FAKE_TOKEN.test'}
    
        response = client.post('/users/sign-in/kakao', content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 200)

    @patch('user.views.requests')
    def test_kakao_sign_in_key_error(self, mocked_request):
        class Fakeresponse:
            def json(self):
                return {
                    'kakao_account': {
                        'profile':   {'nickname':'test'},
                    }
                }
        client             = Client()
        mocked_request.get = MagicMock(return_value = Fakeresponse())
        headers            = {'Authorization':'FAKE_TOKEN.test'}
    
        response = client.post('/users/sign-in/kakao', content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'MESSAGE':'KEY_ERROR'})

    @patch('user.views.requests')
    def test_kakao_sign_in_page_not_found(self, mocked_request):
        class Fakeresponse:
            def json(self):
                return {
                    'kakao_account': {
                        'profile':   {'nickname':'test'},
                        'email':     'test@gmail.com'
                    }
                }
        client             = Client()
        mocked_request.get = MagicMock(return_value = Fakeresponse())
        headers            = {'Authorization':'FAKE_TOKEN.test'}
    
        response = client.post('/users/sign-in/random', content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 404)    

class ProductSizeFollowTest(TestCase):
    def setUp(self):
        user = User(
            first_name = 'origin_first',
            last_name  = 'origin_last',
            email      = 'origin@gmail.com',
            password   = 'Test4321!'
        )
        user.save()
        access_token = jwt.encode(
            {'user_id':user.id}, SECRET_KEY['SECRET_KEY'], ALGORITHM['ALGORITHM']
        ).decode('utf-8')
        return access_token
    
    def tearDown(self):
        User.objects.all().delete()

    def test_product_size_follow_succes(self):
        client = Client()

        data = {
            'product': 1,
            'sizes':   ['4.5', '5', '5.5']
        }
        headers = {"HTTP_Authorization": self.setUp()}

        response = client.post('/users/follow', json.dumps(data), content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 200)

    def test_product_size_follow_page_not_found(self):
        client = Client()

        data = {
            'product': 1,
            'sizes':   ['4.5', '5', '5.5']
        }
        headers = {"HTTP_Authorization": self.setUp()}

        response = client.post('/users/following', json.dumps(data), content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 404)

class SellingList(TestCase):
    def setUp(self):
        user = User(
            first_name = 'origin_first',
            last_name  = 'origin_last',
            email      = 'origin@gmail.com',
            password   = 'Test4321!'
        )
        user.save()
        access_token = jwt.encode(
            {'user_id':user.id}, SECRET_KEY['SECRET_KEY'], ALGORITHM['ALGORITHM']
        ).decode('utf-8')
        return access_token
    
    def tearDown(self):
        User.objects.all().delete()

    def test_selling_list_succes(self):
        client = Client()

        headers = {"HTTP_Authorization": self.setUp()}

        response = client.get('/users/selling-list', content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 200)
    
    def test_selling_list_page_not_found(self):
        client = Client()

        headers = {"HTTP_Authorization": self.setUp()}

        response = client.get('/users/selling', content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 404)

class GoogleSignInTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            email = "helloworld@gmail.com",
            first_name = "hello",
            last_name = "world",
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch('user.views.requests')
    def test_google_sign_in_success(self, mocked_request):
        class FakeResponse:
            def json(self):
                return {
                    "email"      : "helloworld@gmail.com",
                    "given_name" : "Hello",
                    "family_name": "World"
                }

        client             = Client()
        mocked_request.get = MagicMock(return_value = FakeResponse())
        headers            = {'HTTP_Authorization':'random_token_from_google'}
        response           = client.get('/users/sign-in/google', content_type = 'application/json', **headers)
        body               = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body['ACCESS_TOKEN'])

    @patch('user.views.requests')
    def test_google_sign_in_page_not_found(self, mocked_request):
        class FakeResponse:
            def json(self):
                return {
                    "email"      : "helloworld@gmail.com",
                    "given_name" : "Hello",
                    "family_name": "World"
                }

        mocked_request.get = MagicMock(return_value = FakeResponse())
        client             = Client()
        headers            = {'HTTP_Authorization':'random_token_from_google'}
        response = client.get('/users/sign-in/random', content_type = 'application/json', **headers)
        self.assertEqual(response.status_code, 404)

    @patch('user.views.requests')
    def test_google_sign_in_key_error_exception(self, mocked_request):
        class FakeResponse:
            def json(self):
                return dict()

        client             = Client()
        mocked_request.get = MagicMock(return_value = FakeResponse())
        headers            = {'HTTP_Authorization':'random_token_from_google'}
        response           = client.get('/users/sign-in/google', content_type = 'application/json', **headers)
        body               = response.json()
        self.assertEqual(response.status_code, 401)