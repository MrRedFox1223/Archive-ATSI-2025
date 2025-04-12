from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager


STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tags(models.Model):
    pass


class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height"50" />' % (self.image.url))

    def __str__(self):
        return self.title


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")

    title = models.CharField(max_length=100, default="Ticket")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    place = models.CharField(max_length=100, default="Warsaw")

    date_of_event = models.DateField()
    date_of_sales_start = models.DateField()
    date_of_sales_end = models.DateField()

    short_description = models.CharField(max_length=100, default="This is the product")
    description = models.TextField(null=True, blank=True, default="This is the product description")

    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.00")
    old_price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="2.00")

    specification = models.TextField(null=True, blank=True,)
    stock_count = models.IntegerField(default=100)
    tags = TaggableManager(blank=True)

    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")

    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")

    class Meta:
        verbose_name_plural = "Products"
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_of_sales_start__lte=models.F('date_of_event')) & 
                      models.Q(date_of_sales_end__gte=models.F('date_of_event')),
                name='event_date_between_sales_dates'
            )
        ]

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_precentage(self):
        new_price = 100 - ((self.price / self.old_price) * 100)
        return new_price

    def calculate_stock(self, stock_to_remove):
        if self.stock_count - stock_to_remove <= 0:
            self.stock_count = 0
            self.in_stock = False
        else:
            self.stock_count = self.stock_count - stock_to_remove
        self.save()


class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99")

    paid_status = models.BooleanField(default=False, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    sku = ShortUUIDField(null=True, blank=True, length=5, prefix="SKU", max_length=20, alphabet="abcdefgh12345")

    class Meta:
        verbose_name_plural = "Cart Order"


class CartOrderProducts(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99")
    total = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title if self.product else "No product"

    def get_rating(self):
        return self.rating


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mobile = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"
