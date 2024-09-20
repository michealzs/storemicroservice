export function fetchOrderSummary() {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/order/summary/`)
        .then(response => response.json())
        .then(data => renderOrderSummary(data))
        .catch(error => console.log('Error fetching order summary:', error));
}

function renderOrderSummary(order) {
    const orderItems = document.getElementById('order-items');
    orderItems.innerHTML = '';

    order.items.forEach(item => {
        const orderItem = document.createElement('div');
        orderItem.innerHTML = `
            <p>${item.product_name} (${item.quantity}) - ${item.total_price}</p>
        `;
        orderItems.appendChild(orderItem);
    });
}

export function fetchOrderHistory() {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/order/history/`)
        .then(response => response.json())
        .then(data => renderOrderHistory(data))
        .catch(error => console.log('Error fetching order history:', error));
}

function renderOrderHistory(orders) {
    const orderList = document.getElementById('order-list');
    orderList.innerHTML = '';

    orders.forEach(order => {
        const orderItem = document.createElement('div');
        orderItem.innerHTML = `
            <h3>Order #${order.order_number}</h3>
            <p>Status: ${order.status}</p>
            <p>Total: ${order.total}</p>
            <div>
                ${order.items.map(item => `<p>${item.product_name} (${item.quantity})</p>`).join('')}
            </div>
        `;
        orderList.appendChild(orderItem);
    });
}

export function checkout() {
    const apiBaseUrl = '/api';
    
    fetch(`${apiBaseUrl}/order/checkout/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Session-Key': sessionStorage.getItem('session_key') || ''
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('order-success').style.display = 'block';
                document.getElementById('order-number').innerText = data.order_number;
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.log('Error during checkout:', error));
}
