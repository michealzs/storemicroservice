import { fetchProductsByCategory, fetchProductsBySubcategory } from './modules/products.js';
import { fetchCartCount } from './modules/cart.js';
import { fetchOrderSummary, fetchOrderHistory, checkout } from './modules/orders.js';
import { searchProducts } from './modules/search.js';
import { fetchReviews } from './modules/reviews.js';

document.addEventListener("DOMContentLoaded", function() {
    fetchCartCount();             // Load cart count
    fetchOrderSummary();          // Load order summary if applicable
    fetchOrderHistory();          // Load order history if applicable
    searchProducts();             // Set up search functionality
    
    // If the page involves products
    if (document.getElementById('product-list')) {
        fetchProductsByCategory(); // Load products by category
    }

    // If product reviews are needed
    if (document.getElementById('reviews-list')) {
        const productSlug = document.getElementById('reviews-list').dataset.productSlug;
        fetchReviews(productSlug); // Load reviews for a specific product
    }
});
