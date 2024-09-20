export function fetchProductsByCategory() {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/category/products/`)
        .then(response => response.json())
        .then(data => renderProducts(data))
        .catch(error => console.log('Error fetching products by category:', error));
}

export function fetchProductsBySubcategory(slug) {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/subcategory/${slug}/products/`)
        .then(response => response.json())
        .then(data => renderProducts(data))
        .catch(error => console.log('Error fetching products by subcategory:', error));
}

function renderProducts(products) {
    const productList = document.getElementById('product-list');
    productList.innerHTML = '';

    products.forEach(product => {
        const productItem = document.createElement('div');
        productItem.innerHTML = `
            <h2>${product.name}</h2>
            <img src="${product.image}" alt="${product.name}" width="150">
            <p>${product.price}</p>
            ${product.discount_price ? `<p>Discount: ${product.discount_price}</p>` : ''}
            <select id="variant-select-${product.slug}">
                ${product.variants.map(variant => `<option value="${variant.id}">${variant.title} - ${variant.price}</option>`).join('')}
            </select>
            <button onclick="addToCart('${product.slug}')">Add to Cart</button>
        `;
        productList.appendChild(productItem);
    });
}
