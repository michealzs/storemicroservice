from django.contrib import admin, messages
from .shopify import ShopifyAPI
from django.http import HttpResponseRedirect
from django.urls import path
from .models import (
    Product,
    ProductReview,
    Category,
    Subcategory,
    Coupon,
    Order,
    ProductViewLog,
    Cart,
    SearchTerm,
    StripeCharge,
    Refund,
    Return,
    UserProfile,
)

#########################################
#           Product Admin               #
#########################################

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'created_at', 'updated_at')
    list_filter = ['is_active', 'is_featured']
    list_display_links = ('name',)
    list_per_page = 50
    ordering = ['-updated_at']
    search_fields = ['name', 'description', 'meta_keywords', 'meta_description']
    exclude = ('created_at', 'updated_at',)
    readonly_fields = ('created_at', 'updated_at')
    sortable_by = ['created_at', 'updated_at']
    prepopulated_fields = {
        'slug': ('name',),
        'meta_keywords': ('name',),
        'meta_description': ('description',),
    }

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'brand', 'price', 'discount_price', 'quantity', 'description', 'categories', 'meta_keywords', 'meta_description')
        }),
        ('Availability', {
            'fields': ('is_active', 'is_bestseller', 'is_featured')
        }),
        ('Images', {
            'fields': ('image', 'thumbnail1', 'thumbnail2', 'thumbnail3', 'thumbnail4', 'thumbnail5', 'thumbnail6')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        })
    )

    actions = ['make_featured', 'make_bestseller', 'make_inactive']

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark selected products as featured"

    def make_bestseller(self, request, queryset):
        queryset.update(is_bestseller=True)
    make_bestseller.short_description = "Mark selected products as bestsellers"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected products as inactive"

    # Define the custom action
    def load_shopify_products(self, request):
        shop_name = "your_shop_name"  # Should be dynamically passed or obtained
        access_token = "your_access_token"  # Use secure method to obtain
        shopify_api = ShopifyAPI(shop_name, access_token)
        
        try:
            shopify_api.load_products()
            self.message_user(request, "Products loaded successfully", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error loading products: {str(e)}", level=messages.ERROR)
        
        # Redirect back to the product list view
        return HttpResponseRedirect("../")

    # Customize the admin template to add a button
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('load-shopify-products/', self.admin_site.admin_view(self.load_shopify_products), name='load_shopify_products'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['load_shopify_products_url'] = 'admin:load_shopify_products'
        return super(ProductAdmin, self).changelist_view(request, extra_context=extra_context)


admin.site.register(Product, ProductAdmin)


#########################################
#       Product Review Admin            #
#########################################

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'date')
    list_filter = ('is_approved', 'rating', 'date')
    search_fields = ('user__username', 'product__name', 'rating', 'content')
    list_per_page = 20
    date_hierarchy = 'date'
    fieldsets = (
        ('Basic Info', {'fields': ('product', 'user', 'rating', 'content')}),
        ('Status', {'fields': ('is_approved',)}),
        ('Timestamps', {'fields': ('date',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('date',)

    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)

    approve_reviews.short_description = 'Approve selected product reviews'
    disapprove_reviews.short_description = 'Disapprove selected product reviews'

admin.site.register(ProductReview, ProductReviewAdmin)


#########################################
#       Category Admin                  #
#########################################

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_display_links = ('name',)
    list_filter = ('created_at', 'updated_at')
    list_per_page = 20
    ordering = ['name']
    search_fields = ['name', 'description', 'meta_keywords', 'meta_description']
    exclude = ('created_at', 'updated_at',)
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'description')}),
        ('SEO Info', {'fields': ('meta_keywords', 'meta_description')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    make_active.short_description = 'Mark selected categories as active'
    make_inactive.short_description = 'Mark selected categories as inactive'

admin.site.register(Category, CategoryAdmin)


#########################################
#       Subcategory Admin               #
#########################################

class SubcategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')

admin.site.register(Subcategory, SubcategoryAdmin)


#########################################
#           Coupon Admin                #
#########################################

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'discount', 'expiration_date', 'is_approved')
    list_filter = ('is_approved', 'expiration_date')
    search_fields = ('code', 'description', 'discount')
    date_hierarchy = 'expiration_date'
    readonly_fields = ('code', 'discount', 'description')
    fieldsets = (
        ('Basic Info', {'fields': ('code', 'description', 'discount')}),
        ('Status', {'fields': ('is_approved',)}),
        ('Expiration', {'fields': ('expiration_date',)}),
    )

admin.site.register(Coupon, CouponAdmin)


#########################################
#           Order Admin                 #
#########################################

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'created_at', 'payment_status', 'status', 'total', 'tracking_number')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('user', 'total', 'email', 'created_at', 'last_updated', 'phone_number', 'ip_address', 'cart_items',
                       'order_number', 'session', 'coupon', 'payment_status', 'customer_id', 'transaction_id',
                       'customer_name', 'shipping_name', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 
                       'country', 'amount_discount', 'amount_shipping', 'amount_tax', 'ordered')
    fieldsets = (
        ('Order Details', {
            'fields': ('ordered', 'status', 'payment_status', 'order_number', 'tracking_number', 'created_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'email', 'phone_number', 'user',)
        }),
        ('Shipping Details', {
            'fields': ('shipping_name', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Cart Details', {
            'fields': ('cart_items', 'total', 'coupon', 'amount_discount', 'amount_shipping', 'amount_tax')
        }),
        ('Additional Details', {
            'fields': ('last_updated', 'transaction_id', 'customer_id', 'ip_address', 'session')
        })
    )

    def has_add_permission(self, request):
        return False


#########################################
#       Product View Log Admin           #
#########################################

class ProductViewLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'viewed_at', 'ip_address', 'tracking_id')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name', 'ip_address')

admin.site.register(ProductViewLog, ProductViewLogAdmin)


#########################################
#               Cart Admin              #
#########################################

class CartAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'get_quantity', 'get_user')
    list_filter = ('user',)
    search_fields = ('product__name',)

    def get_product_name(self, obj):
        return obj.product.name if obj.product else 'No Product'

    get_product_name.short_description = 'Product'

    def get_quantity(self, obj):
        return obj.quantity

    get_quantity.short_description = 'Quantity'

    def get_user(self, obj):
        return obj.user.username if obj.user else 'Anonymous'

    get_user.short_description = 'User'

admin.site.register(Cart, CartAdmin)

#########################################
#           User Profile Admin          #
#########################################

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email')
    search_fields = ('user__username', 'email')

admin.site.register(UserProfile, UserProfileAdmin)


#########################################
#           Search Term Admin           #
#########################################

class SearchTermAdmin(admin.ModelAdmin):
    list_display = ('query', 'search_date', 'user')
    list_filter = ('user',)
    search_fields = ('query',)
    readonly_fields = ('search_date', 'user')

admin.site.register(SearchTerm, SearchTermAdmin)


#########################################
#           Stripe Charge Admin         #
#########################################

@admin.register(StripeCharge)
class StripeChargeAdmin(admin.ModelAdmin):
    list_display = ('stripe_charge_id', 'amount', 'currency', 'paid', 'status')
    list_filter = ('currency', 'paid', 'status')
    search_fields = ('stripe_charge_id', 'description')
    readonly_fields = ('stripe_charge_id', 'amount', 'currency', 'description', 'paid', 'status', 'details')


#########################################
#               Refund Admin            #
#########################################

class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'refund_amount', 'reason_for_refund', 'refund_date')
    list_filter = ('refund_date',)
    search_fields = ('order__id', 'reason_for_refund')

admin.site.register(Refund, RefundAdmin)


#########################################
#               Return Admin            #
#########################################

class ReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'return_date', 'reason_for_return', 'notes')
    list_filter = ('order', 'return_date')
    search_fields = ('order__id', 'reason_for_return')
    ordering = ('-return_date',)

admin.site.register(Return, ReturnAdmin)