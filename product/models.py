from django.db import models

class MainCategory(models.Model):
    name = models.CharField(max_length = 64, null = False)

    class Meta:
        db_table = 'main_categories'

class SubCategory(models.Model):
    name          = models.CharField(max_length = 64, null = False)
    main_category = models.ForeignKey(MainCategory, on_delete = models.CASCADE)

    class Meta:
        db_table = 'sub_categories'

class Specific(models.Model):
    name         = models.CharField(max_length = 64, null = False)
    sub_category = models.ForeignKey(SubCategory, on_delete = models.CASCADE)

    class Meta:
        db_table = 'specifics'

class Product(models.Model):
    name          = models.CharField(max_length = 256, null = False)
    description   = models.TextField(null = True)
    ticker        = models.CharField(max_length = 128, null = False)
    style         = models.CharField(max_length = 32, null = False)
    retail_price  = models.DecimalField(max_digits = 8, decimal_places = 2, null = False)
    colorway      = models.CharField(max_length = 128, null = False)
    release_date  = models.ForeignKey('ReleaseDate', on_delete = models.CASCADE)
    size_type     = models.ForeignKey('SizeType', on_delete = models.CASCADE)
    category      = models.ForeignKey(Specific, on_delete = models.CASCADE)
    product_size  = models.ManyToManyField('Size', through = 'ProductSize', related_name = 'product_with_size')
    average_price = models.IntegerField(null = True)
    volatility    = models.DecimalField(max_digits = 5, decimal_places = 1, null = True)
    price_premium = models.IntegerField(null = True)

    class Meta:  
        db_table = "products"

class SizeType(models.Model):
    name = models.CharField(max_length = 32, null = False)

    class Meta:
        db_table = "size_types"

class ReleaseDate(models.Model):
    date = models.DateField(null = False)

    class Meta:
        db_table = "release_dates"

class Image(models.Model):
    product    = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = 'image_with_product')
    image_type = models.ForeignKey('ImageType', on_delete = models.CASCADE)
    url        = models.TextField()

    class Meta:
        db_table = "images"

class ImageType(models.Model):
    name = models.CharField(max_length = 16, null = False)

    class Meta:
        db_table = "image_types"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    size    = models.ForeignKey('Size', on_delete = models.CASCADE)

    class Meta:
        db_table = "product_sizes"

class Size(models.Model):
    name = models.CharField(max_length = 16, null = False)

    class Meta:
        db_table = "sizes"