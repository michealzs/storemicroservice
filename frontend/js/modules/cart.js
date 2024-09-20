export function fetchCartCount() {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/cart/count/`)
        .then(response => response.json())
        .then(data => {
            const cartCount = document.getElementById('cart-count');
            cartCount.textContent = data.count;
        })
        .catch(error => console.log('Error fetching cart count:', error));
}

export function addToCart(slug, variantId) {
    const apiBaseUrl = '/api';
    const variantSelect = document.getElementById(`variant-select-${slug}`);
    const selectedVariantId = variantSelect ? variantSelect.value : variantId;

    fetch(`${apiBaseUrl}/cart/add/${slug}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Session-Key': sessionStorage.getItem('session_key') || ''
        },
        body: JSON.stringify({ variant_id: selectedVariantId })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchCartCount();  // Refresh cart count
        })
        .catch(error => console.log('Error adding to cart:', error));
}
