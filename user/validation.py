import re

from django.core.exceptions import ValidationError

def is_email(email):
    regex = re.compile(r'^\w+([-_.]?\w+)\@\w+\.\w{2,3}')
    if not regex.match(email):
        raise ValidationError(message = None)

def is_password(password):
    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}')
    if not regex.match(password):
        raise ValidationError(message = None)