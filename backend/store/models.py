
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as gl
from django.utils import timezone
from datetime import datetime
import uuid



###################################################
#               Managers                          #
###################################################
class StoreManager(models.Manager):
    def queryset(self):
        return super().get_queryset()

    def featured(self):
        return self.filter(is_featured=True, is_active=True) # self.get_queryset().filter(is_active=True, is_featured=True)

    def approved(self):
        return self.filter(is_active=True) # self.get_queryset().filter(is_approved=True)

    def active(self):
        return self.filter(is_active=True) # self.get_queryset().filter(is_active=True)

###################################################
#               Category                          #
###################################################

class Category(models.Model):
    """ Categories are created based on Shopify product tags """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, help_text='URL-friendly version of the category name')
    description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField("Meta Keywords", max_length=255, help_text='SEO keywords for meta tag', blank=True)
    meta_description = models.CharField("Meta Description", max_length=255, help_text='Content for description meta tag', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    objects = StoreManager()

###################################################
#               Subcategory                       #
###################################################

class Subcategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, help_text='URL-friendly version of the subcategory name')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    meta_keywords = models.CharField("Meta Keywords", max_length=255, help_text='SEO keywords for meta tag')
    meta_description = models.CharField("Meta Description", max_length=255, help_text='Content for description meta tag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    objects = StoreManager()


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:subcategory_list", kwargs={'slug': self.slug})

    class Meta:
        db_table = 'subcategories'
        ordering = ['-created_at']
        verbose_name_plural = 'Subcategories'

###################################################
#               Product                           #
###################################################  

class Product(models.Model):
    """ Product is linked to multiple variants and categories """
    shopify_id = models.CharField(max_length=50, unique=True, null=True)  # Shopify product ID
    name = models.CharField(max_length=100, unique=True)  # Product title
    slug = models.SlugField(max_length=100, unique=True, help_text='Slug value for the product URL')
    vendor = models.CharField(max_length=100, blank=True)  # Product vendor
    description = models.TextField()  # Product description (body_html)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price (from first variant)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)  # Discount price (compare_at_price)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='products', blank=True)  # Linked to categories (tags)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_description = models.CharField(max_length=255, help_text='Meta tag description', blank=True)
    meta_keywords = models.CharField(max_length=255, help_text='SEO keywords separated by commas', blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        verbose_name_plural = 'products'

    def __str__(self):
        return f"{self.quantity} of {self.name}"

    def get_absolute_url(self):
        return reverse("store:product_detail", kwargs={'slug': self.slug})

    def sale_price(self):
        if self.discount_price > 0.00 and self.price > self.discount_price:
            return self.discount_price
        return self.price #return None

    def unit_amount(self):
        return int(str(self.sale_price()).replace('.', ''))

    def generate_sku(self):
        return str(uuid.uuid4().hex)[:10]

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        self.meta_keywords = ','.join(self.name.split()) # Set the meta_keywords field to a comma-separated string of words in the product name
        self.meta_description = ','.join(self.name.split()) # Set the meta_keywords field to a comma-separated string of words in the product name
        super().save(*args, **kwargs) # Call the superclass save method to save the model instance

    objects = StoreManager()

class ProductVariant(models.Model):
    """ Variants are linked to a product """
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    variant_id = models.CharField(max_length=50, unique=True)  # Shopify variant ID
    title = models.CharField(max_length=100)  # Variant title
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Variant price
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Discount price
    inventory_quantity = models.IntegerField(default=0)  # Inventory quantity of the variant

    def __str__(self):
        return f"{self.title} - {self.product.name}"


class ProductImage(models.Model):
    """ Images can be linked to a product and optionally to a variant """
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500)  # Image URL
    variant = models.ForeignKey(ProductVariant, related_name='images', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.image_url


###################################################
#               Product Review                    #
###################################################

class ProductReview(models.Model):
    RATINGS = [
        (5, 'Excellent'),
        (4, 'Good'),
        (3, 'Average'),
        (2, 'Poor'),
        (1, 'Terrible'),
    ]
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    date = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(choices=RATINGS, default=5)
    is_approved = models.BooleanField(default=True)
    content = models.TextField()

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-date']

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'

###################################################
#               Product View Log                  #
###################################################

class ProductViewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='view_logs')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='view_logs')
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(protocol='both', null=True, blank=True)
    tracking_id = models.CharField(max_length=50, default='', blank=True)

    class Meta:
        ordering = ['-viewed_at']
        verbose_name_plural = 'Product View Logs'

    def __str__(self):
        return f'{self.user.username if self.user else "Anonymous"} viewed {self.product.name}'

###################################################
#               Coupon                            #
###################################################

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100)
    discount = models.FloatField(validators=[MinValueValidator(0)])
    expiration_date = models.DateTimeField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-expiration_date']

    def __str__(self):
        return self.code
    
###################################################
#               Cart                              #
###################################################

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cart {self.id} for {self.user.username if self.user else "Anonymous"}'

    def get_total(self):
        return sum(item.get_final_price() for item in self.items.all())

    def get_item_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,null=True, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    session = models.CharField(max_length=50, default='', blank=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product.name} ({self.quantity})'

    def get_total(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total()

    def get_absolute_url(self):
        return self.product.get_absolute_url()


###################################################
#               Order                             #
###################################################

class Order(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('R', 'Returned')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='orders')
    email = models.EmailField(max_length=254, null=True, blank=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    cart_items = models.ManyToManyField('CartItem', related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=False)
    last_updated = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    order_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    tracking_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    session = models.CharField(max_length=50, default='', blank=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=50, blank=False, null=True)
    customer_id = models.CharField(max_length=50, blank=False, null=True)
    transaction_id = models.CharField(max_length=50, blank=False, null=True)
    customer_name = models.CharField(max_length=50, blank=False, null=True)
    shipping_name = models.CharField(max_length=50, blank=False, null=True)
    address_line_1 = models.CharField(max_length=255, blank=False, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=55, blank=False, null=True)
    state = models.CharField(max_length=55, blank=False, null=True)
    country = models.CharField(max_length=55, blank=False, null=True)
    postal_code = models.CharField(max_length=20, blank=False, null=True)
    amount_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)
    amount_shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)
    amount_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.00)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order {self.pk}'

    def get_total(self):
        total = sum(item.get_final_price() for item in self.cart_items.all())
        if self.coupon:
            total -= self.coupon.discount
        total += self.amount_shipping + self.amount_tax - self.amount_discount
        return total

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(uuid.uuid4()).replace('-', '').upper()[:12]  # Generates a unique order number
        self.total = self.get_total()  # Calculate total before saving
        super().save(*args, **kwargs)


###################################################
#                Shipping Address                 #
###################################################

# class ShippingAddress(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     address_line_1 = models.CharField(max_length=255)
#     address_line_2 = models.CharField(max_length=255, blank=True, null=True)
#     city = models.CharField(max_length=255)
#     state = models.CharField(max_length=255)
#     postal_code = models.CharField(max_length=20)

#     def __str__(self):
#         return f'{self.user.username} Shipping Address'

#     class Meta:
#         verbose_name_plural = 'Shipping Addresses'



###################################################
#                User Profile                     #
###################################################

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, unique=True, null=True)
    id = models.IntegerField(default=0, null=False, primary_key=True)

    def __str__(self):
        return f'{self.user.first_name} Profile'

###################################################
#                Search                            #
###################################################

class SearchTerm(models.Model):
    query = models.CharField(max_length=255)
    search_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-search_date']

    def __str__(self):
        return self.query

###################################################
#                Stripe                           #
###################################################

class StripeCharge(models.Model):
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    description = models.TextField()
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=255)
    details = models.CharField(max_length=255)

    def __str__(self):
        return f'Stripe Charge {self.stripe_charge_id} - {self.amount} {self.currency}'

###################################################
#                  Refund                         #
###################################################

class Refund(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason_for_refund = models.CharField(max_length=255)
    refund_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Refund {self.id} for Order {self.order.id}'

###################################################
#                  Return                         #
###################################################

class Return(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    return_date = models.DateTimeField(auto_now_add=True)
    reason_for_return = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'Return {self.id} for Order {self.order.id}'

###################################################
#                  Popular                        #
###################################################

class PopularProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    cart_count = models.PositiveIntegerField(gl('Cart Count'), null=True)
    buys_count = models.PositiveIntegerField(gl('Buys Count'), null=True)
    
    objects = models.Manager()  # Default manager
    active = StoreManager().active

    class Meta:
        verbose_name = gl('Popular Product')
        verbose_name_plural = gl('Popular Products')

    def __str__(self):
        return f"{self.product.name} ({self.cart_count} views)"