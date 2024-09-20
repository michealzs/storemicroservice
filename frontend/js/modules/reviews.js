export function fetchReviews(productSlug) {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/product/${productSlug}/reviews/`)
        .then(response => response.json())
        .then(data => renderReviews(data))
        .catch(error => console.log('Error fetching reviews:', error));
}

function renderReviews(reviews) {
    const reviewsList = document.getElementById('reviews-list');
    reviewsList.innerHTML = '';

    reviews.forEach(review => {
        const reviewItem = document.createElement('div');
        reviewItem.innerHTML = `
            <h3>${review.user}</h3>
            <p>Rating: ${review.rating}</p>
            <p>${review.content}</p>
        `;
        reviewsList.appendChild(reviewItem);
    });
}
