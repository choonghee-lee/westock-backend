from django.db  import models

from .validation import is_email, is_password

class User(models.Model):
    first_name   = models.CharField(max_length = 64)
    last_name    = models.CharField(max_length = 64)
    email        = models.CharField(max_length = 64, validators = [is_email])
    password     = models.CharField(max_length = 64, validators = [is_password])
    membership   = models.PositiveIntegerField(default = 1)
    product_size = models.ManyToManyField('product.ProductSize', through = 'Follow')

    class Meta:
        db_table = 'users'

class Address(models.Model):
    user         = models.ForeignKey('User', on_delete = models.CASCADE)
    info_type    = models.CharField(max_length = 64)
    country      = models.CharField(max_length = 64)
    first_name   = models.CharField(max_length = 64)
    last_name    = models.CharField(max_length = 64)
    main_address = models.CharField(max_length = 512)
    sub_address  = models.CharField(max_length = 512, null = True, blank = True)
    city         = models.CharField(max_length = 128)
    state        = models.CharField(max_length = 128)
    postal_code  = models.CharField(max_length = 64)
    phone        = models.CharField(max_length = 64)
    ccic         = models.CharField(max_length = 128, null = True, blank = True)

    class Meta:
        db_table = 'addresses'

class Card(models.Model):
    user        = models.ForeignKey('User', on_delete = models.CASCADE)
    card_number = models.CharField(max_length = 128)
    expiration  = models.CharField(max_length = 64)

    class Meta:
        db_table = 'cards'

class Payout(models.Model):
    user        = models.ForeignKey('User', on_delete = models.CASCADE)
    card_number = models.CharField(max_length = 128)
    expiration  = models.CharField(max_length = 64)

class Follow(models.Model):
    user         = models.ForeignKey('User', on_delete = models.CASCADE)
    product_size = models.ForeignKey('product.ProductSize', on_delete = models.CASCADE)

    class Meta:
        db_table = 'follows'
