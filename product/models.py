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
    name         = models.CharField(max_length = 256, null = False)
    description  = models.CharField(max_length = 4096, null = True)
    style        = models.CharField(max_length = 32, null = False)
    retali_price = models.IntegerField(null = True)
    colorway     = models.CharField(max_length = 128, null = False)
    release_date = models.ForeignKey('ReleaseDate', on_delete = models.CASCADE)
    size_type    = models.ForeignKey('SizeType', on_delete = models.CASCADE)
    category     = models.ForeignKey(Specific, on_delete = models.CASCADE)
    product_size = models.ManyToManyField('Size', through = 'ProductSize', related_name = 'product_with_size')

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
    url        = models.CharField(max_length = 4096, null = False)

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
