from django.db import models

class Status(models.Model):
    name = models.CharField(max_length = 64)

    class Meta:
        db_table = 'statuses'

class Ask(models.Model):
    price           = models.DecimalField(max_digits = 10, decimal_places = 4)
    expired_date    = models.DateTimeField()
    status          = models.ForeignKey('Status', on_delete = models.CASCADE)
    product_size    = models.ForeignKey('product.ProductSize', on_delete = models.CASCADE)
    created_at      = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        db_table = 'asks'

class UserAsk(models.Model):
    ask  = models.ForeignKey('Ask', on_delete = models.CASCADE)
    user = models.ForeignKey('user.User', on_delete = models.CASCADE)

    class Meta:
        db_table = 'user_asks'

class Bid(models.Model):
    price           = models.DecimalField(max_digits = 10, decimal_places = 4)
    expired_date    = models.DateTimeField()
    status          = models.ForeignKey('Status', on_delete = models.CASCADE)
    user            = models.ForeignKey('user.User', on_delete = models.CASCADE)
    product_size    = models.ForeignKey('product.ProductSize', on_delete = models.CASCADE)
    created_at      = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        db_table = 'bids'

class Order(models.Model):
    date = models.DateTimeField()
    bid  = models.ForeignKey('Bid', on_delete = models.CASCADE)
    ask  = models.ForeignKey('Ask', on_delete = models.CASCADE)

    class Meta:
        db_table = 'orders'