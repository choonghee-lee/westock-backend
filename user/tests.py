import json, bcrypt

from django.test import TestCase, Client

from .models     import User

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