"""
Serialization: Convert Django model instances or querysets into JSON, XML, or other formats for APIs.
Deserialization: Convert JSON or other serialized data back into Django model instances or Python objects.
Validation: Validate incoming data before saving it to the database.
"""
from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Order, Product
from .models import (
    Category, Subcategory, Product, ProductVariant, ProductImage,
    ProductReview, Cart, CartItem, Order, Coupon, UserProfile, SearchTerm,
    StripeCharge, Refund, Return, PopularProduct
)

###################################################
#               Category Serializer               #
###################################################
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


###################################################
#               Subcategory Serializer            #
###################################################
class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nest Category serializer

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'description', 'slug']

###################################################
#               Product Serializer                #
###################################################
class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)  # Nest Category serializer

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'slug', 'image']


###################################################
#               Product Variant Serializer        #
###################################################
class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nest Product serializer

    class Meta:
        model = ProductVariant
        fields = '__all__'


###################################################
#               Product Image Serializer          #
###################################################
class ProductImageSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nest Product serializer

    class Meta:
        model = ProductImage
        fields = '__all__'


###################################################
#               Product Review Serializer         #
###################################################
class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nest Product serializer

    class Meta:
        model = ProductReview
        #fields = '__all__'
        fields = ['rating', 'comment', 'created_at']  # Add any additional fields if necessary
        read_only_fields = ['user', 'product']


###################################################
#               Cart Serializer                   #
###################################################
class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show user as string
    items = serializers.SerializerMethodField()  # Custom field to get cart items

    class Meta:
        model = Cart
        fields = '__all__'

    def get_items(self, obj):
        return CartItemSerializer(obj.items.all(), many=True).data


###################################################
#               Cart Item Serializer              #
###################################################
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nest Product serializer

    class Meta:
        model = CartItem
        fields = '__all__'


###################################################
#               Order Serializer                  #
###################################################
class OrderSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)  # Nest CartItem serializer
    user = serializers.StringRelatedField(read_only=True)  # Show user as string

    class Meta:
        model = Order
        fields = '__all__'


###################################################
#               Coupon Serializer                 #
###################################################
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


###################################################
#               User Profile Serializer           #
###################################################
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show user as string

    class Meta:
        model = UserProfile
        fields = '__all__'


###################################################
#               Search Term Serializer            #
###################################################
class SearchTermSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show user as string

    class Meta:
        model = SearchTerm
        fields = '__all__'


###################################################
#               Stripe Charge Serializer          #
###################################################
class StripeChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeCharge
        fields = '__all__'


###################################################
#               Refund Serializer                 #
###################################################
class RefundSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)  # Nest Order serializer

    class Meta:
        model = Refund
        fields = '__all__'


###################################################
#               Return Serializer                 #
###################################################
class ReturnSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)  # Nest Order serializer

    class Meta:
        model = Return
        fields = '__all__'


###################################################
#               Popular Product Serializer        #
###################################################
class PopularProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Nest Product serializer

    class Meta:
        model = PopularProduct
        #fields = '__all__'
        fields = ['name', 'description', 'price']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'email', 'first_name', 'last_name', 'date_of_birth']

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'categories']