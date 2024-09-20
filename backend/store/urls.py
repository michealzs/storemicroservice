from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, SubcategoryViewSet, ProductReviewViewSet,
    OrderViewSet, PopularProductViewSet, UserProfileViewSet, 
    HomeView, SearchResultsView, UserProfileLoginView, Logout, 
    ForgotPasswordView, OrderSuccessView, cart, google_base, robots_txt
    UserProfileView, SignupView, LogoutView, UserProfileUpdateView,
    PasswordChangeView, ForgotPasswordView, ConfirmThePasswordResetView,
    OrderHistoryView, SearchResultsView, navbar_data
)

app_name = 'store'

# Create a router and register the viewsets with it
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'subcategories', SubcategoryViewSet, basename='subcategories')
router.register(r'product-reviews', ProductReviewViewSet, basename='product-reviews')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'popular-products', PopularProductViewSet, basename='popular-products')
router.register(r'profile', UserProfileViewSet, basename='profile')

# Add the remaining URLs outside the router
urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Home view
    path('api/navbar/', navbar_data, name='navbar-data'),
    path('search/', SearchResultsView.as_view(), name='search'),  # Search functionality
    path('login/', UserProfileLoginView.as_view(), name='login'),  # Login view
    path('logout/', Logout.as_view(), name='logout'),  # Logout view
    path('passwordreset/', ForgotPasswordView.as_view(), name='passwordreset'),  # Password reset
    path('order/success/', OrderSuccessView.as_view(), name='order_success'),  # Order success page
    path('cart/', cart.view_cart, name='cart'),  # Cart functionality
    path('add-to-cart/<slug>/', cart.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', cart.remove_from_cart, name='remove-from-cart'),
    path('checkout/', cart.checkout, name='checkout'),  # Checkout page
    path('order-summary/', cart.view_cart, name='order-summary'),
    path('google_base.xml/', google_base, name='google_base'),  # Google base
    path('robots.txt/', robots_txt, name='robots_txt'),  # Robots.txt
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('api/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('api/password/reset/', ForgotPasswordView.as_view(), name='password_reset'),
    path('api/password/reset/confirm/<uidb64>/<token>/', ConfirmThePasswordResetView.as_view(), name='password_reset_confirm'),
    path('api/orders/', OrderHistoryView.as_view(), name='order_history'),
    path('api/search/', SearchResultsView.as_view(), name='search'),
    path('api/products/', ActiveProductListView.as_view(), name='active_products'),
    path('api/products/featured/', FeaturedProductListView.as_view(), name='featured_products'),
    path('api/categories/<slug:slug>/products/', CategoryProductListView.as_view(), name='category_products'),
    path('api/categories/<slug:category_slug>/subcategories/<slug:slug>/', SubcategoryDetailView.as_view(), name='subcategory_detail'),
    path('api/categories/<slug:category_slug>/subcategories/', SubcategoryListView.as_view(), name='subcategory_list'),
    path('api/products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('', include(router.urls)),  # Include all router-generated URLs
]