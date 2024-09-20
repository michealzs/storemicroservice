export function searchProducts() {
    const apiBaseUrl = '/api';
    const searchInput = document.getElementById('search-query');

    document.getElementById('search-query').addEventListener('input', function() {
        const query = searchInput.value;
        if (query) {
            fetch(`${apiBaseUrl}/products/search/?q=${query}`)
                .then(response => response.json())
                .then(data => renderSearchResults(data.results))
                .catch(error => console.log('Error searching products:', error));
        }
    });
}

function renderSearchResults(products) {
    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = '';

    products.forEach(product => {
        const productItem = document.createElement('div');
        productItem.innerHTML = `
            <h2>${product.name}</h2>
            <p>${product.price}</p>
        `;
        searchResults.appendChild(productItem);
    });
}
