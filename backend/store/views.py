import time
import hashlib
from uuid import uuid4
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
import stripe

from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

from .models import ProductReview, Product, PopularProduct, CartItem, Order, Subcategory, Category, UserProfile
from .serializers import ProductReviewSerializer, PopularProductSerializer, ProductSerializer, SubcategorySerializer, OrderSerializer, UserProfileSerializer, UpdateUserProfileSerializer

# Other specific imports based on microservice usage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category


@api_view(['GET'])
def navbar_data(request):
    # Fetch categories from the Category model
    categories = [
        {
            "name": category.name,
            "slug": category.slug,
            "url": f"/category/{category.slug}/"
        }
        for category in Category.objects.all()
    ]

    # Cart item count (you may need to replace this with the actual logic for fetching cart item count)
    cart_item_count = 0  # Placeholder logic for cart item count

    # User authentication data
    user_data = {
        "is_authenticated": request.user.is_authenticated,
        "profile_url": "/store/profile" if request.user.is_authenticated else None,
        "logout_url": "/store/logout" if request.user.is_authenticated else None,
        "login_url": "/store/login" if not request.user.is_authenticated else None,
        "signup_url": "/store/signup" if not request.user.is_authenticated else None,
    }

    # Return the data as JSON
    return Response({
        "categories": categories,
        "cart_item_count": cart_item_count,
        "user_data": user_data,
    })


class SessionView(APIView):
    def get(self, request, *args, **kwargs):
        ip = request.META.get('HTTP_X_REAL_IP', '')
        session_key = request.session.session_key

        if not request.session.exists(session_key):
            timestamp = str(time.time())
            unique_string = ip + timestamp
            unique_id = hashlib.sha256(unique_string.encode()).hexdigest()
            request.session.create()
            request.session['visitor_id'] = unique_id
            return Response({"message": "New session created", "session_key": request.session.session_key})
        else:
            return Response({"message": "Existing session", "session_key": request.session.session_key})

class AddToCartView(APIView):
    def post(self, request, slug):
        # Get the session key from the session service
        session_key = request.headers.get('Session-Key')

        product = get_object_or_404(Product, slug=slug)
        order_item, created = CartItem.objects.get_or_create(
            product=product,
            session=session_key,
            ordered=False
        )

        existing_order = Order.objects.filter(session=session_key, ordered=False).first()

        if existing_order:
            if existing_order.cart_items.filter(product__slug=slug).exists():
                order_item.quantity += 1
                order_item.save()
                return Response({"message": "Product quantity updated."})
            else:
                existing_order.cart_items.add(order_item)
                return Response({"message": "Product added to cart."})
        else:
            order = Order.objects.create(
                session=session_key,
                ip_address=request.META.get('HTTP_X_REAL_IP', ''),
                last_updated=timezone.now()
            )
            order.cart_items.add(order_item)
            return Response({"message": "New order created and product added to cart."})


class UserLoginAPI(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(UserLoginAPI, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'user_id': token.user_id,
            'email': token.user.email
        })
    

class GenerateOrderNumberView(APIView):
    def get(self, request, *args, **kwargs):
        prefix = "ORD"
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        timestamp = timestamp[3:]
        random_string = str(uuid4().int)[:9]
        order_number = f"{prefix}{timestamp}{random_string}"

        while Order.objects.filter(order_number=order_number).exists():
            random_string = str(uuid4().int)[:8]
            order_number = f"{prefix}{timestamp}{random_string}"

        return Response({"order_number": order_number})
    

class OrderSuccessAPI(APIView):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        order = Order.objects.get(session=session['metadata']['session_number'])
        order.ordered = True
        order.save()
        return Response({'message': 'Order successfully completed'})

class ActiveProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    pagination_class = None  # Add custom pagination if needed

    def get(self, request, *args, **kwargs):
        print(50 * '8', '\n', request.META.get('HTTP_X_REAL_IP'), "Just Visited US", '\n', 50 * '8')
        
        if request.user.is_authenticated:
            print('pure user ==>', request.user)
            print('pure username ==>', request.user.username)
        else:
            print("<== User is not Authenticated ==>")
        
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        featured_products = Product.objects.filter(is_featured=True, is_active=True)
        response.data['featured_products'] = ProductSerializer(featured_products, many=True).data
        return response

class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

class FeaturedProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_featured=True, is_active=True)
    serializer_class = ProductSerializer
    pagination_class = None  # Add custom pagination if needed

class CategoryProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        category = get_object_or_404(Category, slug=category_slug)
        return Product.objects.filter(categories=category, is_active=True)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        response.data['category'] = {
            "id": category.id,
            "name": category.name,
            "description": category.description
        }
        response.data['featured_products'] = ProductSerializer(Product.objects.filter(is_featured=True), many=True).data
        return response

class SubcategoryDetailView(generics.RetrieveAPIView):
    serializer_class = SubcategorySerializer

    def get_object(self):
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('slug')
        return get_object_or_404(Subcategory, category__slug=category_slug, slug=subcategory_slug)


class SubcategoryListView(generics.ListAPIView):
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        return category.subcategories.all()


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        print(50 * '^|^', '\n', "User accessing product details", '\n', 50 * '^|^')
        return super().get(request, *args, **kwargs)

class ActiveProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination  # Custom pagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        serializer.save()


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"})


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class PasswordChangeView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=400)

        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password changed successfully"})

class ForgotPasswordView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('store:home')
    from_email = settings.DEFAULT_FROM_EMAIL


class ConfirmThePasswordResetView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('store:home')

    def form_valid(self, form):
        messages.info(self.request, 'Your password has been successfully reset.')
        return super().form_valid(form)


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    

# Checkout APIView
class CheckoutAPIView(APIView):
    def get(self, request, *args, **kwargs):
        session_key = request.session.session_key
        order_items = CartItem.objects.filter(session=session_key, ordered=False)
        if order_items.exists():
            order = Order.objects.get(session=session_key, ordered=False)
            context = {
                'order_items': order_items,
                'order': order,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key
        try:
            order = Order.objects.get(session=session_key, ordered=False)
            order_items = order.order_items.all()

            if order_items.exists():
                line_items = []
                for item in order_items:
                    line_items.append({
                        'name': item.product.name,
                        'description': item.product.description,
                        'images': [item.product.image.url],
                        'amount': int(item.product.price * 100),
                        'currency': 'usd',
                        'quantity': item.quantity,
                        'adjustable_quantity': {
                            'enabled': True,
                            'minimum': 1,
                            'maximum': 10,
                        },
                    })

                session = stripe.checkout.Session.create(
                    billing_address_collection="required",
                    customer_creation="always",
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=line_items,
                    success_url=request.build_absolute_uri(reverse_lazy('checkout_success')),
                    cancel_url=request.build_absolute_uri(reverse_lazy('checkout')),
                    shipping_options=[
                        {
                            'shipping_rate_data': {
                                'type': 'fixed_amount',
                                'fixed_amount': {'amount': 0, 'currency': 'usd'},
                                'display_name': 'Free shipping',
                                'delivery_estimate': {
                                    'minimum': {'unit': 'business_day', 'value': 5},
                                    'maximum': {'unit': 'business_day', 'value': 7},
                                },
                            }
                        },
                        {
                            'shipping_rate_data': {
                                'type': 'fixed_amount',
                                'fixed_amount': {'amount': 15 * 100, 'currency': 'usd'},
                                'display_name': 'Next day air',
                                'delivery_estimate': {
                                    'minimum': {'unit': 'business_day', 'value': 1},
                                    'maximum': {'unit': 'business_day', 'value': 1},
                                },
                            }
                        },
                    ]
                )

                return Response({"checkout_url": session.url}, status=status.HTTP_303_SEE_OTHER)
            else:
                return Response({"error": "You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"error": "No active order found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchResultsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | Q(categories__name__icontains=query)
            )
        return Product.objects.none()

# Popular Product List APIView
class PopularProductListAPIView(ListAPIView):
    queryset = PopularProduct.objects.all()
    serializer_class = PopularProductSerializer
    permission_classes = [IsAdminUser]

# Product Review APIView
class ProductReviewCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response({'message': 'Thank you for submitting a review.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Robots.txt view
def robots_txt(request):
    content = "User-agent: *\nDisallow: /admin/\nDisallow: /accounts/\nDisallow: /static/\nDisallow: /media/"
    return HttpResponse(content, content_type='text/plain')

# Google Base XML API
def google_base(request):
    products = Product.active.all()
    template = loader.get_template("marketing/google_base.xml")
    xml = template.render({'products': products})
    return HttpResponse(xml, content_type="application/xml")


# Implement db cacheing