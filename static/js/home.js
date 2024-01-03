// Create a WebSocket connection to the server
let socket = new WebSocket('ws://' + window.location.host + '/ws/sales/');

// Event listener for when the WebSocket connection is opened
socket.addEventListener('open', (event) => {
    // Uncomment the following line to log the WebSocket connection opened event
    // console.log('WebSocket connection opened:', event);
});

// Event listener for when a message is received from the server
socket.addEventListener('message', (event) => {
    // Parse the received JSON data
    const data = JSON.parse(event.data);

    // Uncomment the following line to log the received data
    // console.log('Received data:', data);

    // Check the type of the received data
    if (data.type === 'record_sale') {
        // Extract sale data from the received message
        const saleData = data.sale_data;

        // Uncomment the following line to log the sale type
        // console.log('Sale type:', saleData.success ? 'success' : 'failure');

        // Display success or failure message based on sale result
        if (saleData.success) {
            const productName = saleData.product_name;
            const productPrice = saleData.product_price;
            displaySuccessMessage(productName, productPrice);
        } else {
            displayFailureMessage();
        }
    }
});

// Event listener for when the WebSocket connection is closed
socket.addEventListener('close', (event) => {
    // Uncomment the following line to log the WebSocket connection closed event
    // console.log('WebSocket connection closed:', event);
    
    // Display failure message and reload the page
    displayFailureMessage();
    reloadPage();
});

// Function to reload the page after a delay
function reloadPage() {
    setTimeout(() => {
        location.reload(true);
    }, 2000); // Reload after 2 seconds (adjust the delay as needed)
}

// Function to display a success message with a specified style
function displaySuccessMessage(productName, productPrice) {
    // Create a success message element
    const successMessage = createMessageElement(
        `Sale confirmed for ${productName} @ Ksh ${productPrice}`,
        '#001F3F', // Background color
        '#FFD700'  // Text color
    );
    
    // Append the success message element to the document body
    document.body.appendChild(successMessage);

    // Remove the success message element after a delay
    setTimeout(() => {
        document.body.removeChild(successMessage);
    }, 2000);
}

// Function to display a failure message with a specified style
function displayFailureMessage() {
    // Create a failure message element
    const failureMessage = createMessageElement(
        'Sale didn\'t happen',
        '#FF0000', // Background color
        '#FFFFFF'  // Text color
    );
    
    // Append the failure message element to the document body
    document.body.appendChild(failureMessage);

    // Remove the failure message element after a delay
    setTimeout(() => {
        document.body.removeChild(failureMessage);
    }, 2000);
}

// Function to create a message element with specified text and style
function createMessageElement(text, backgroundColor, textColor) {
    const messageElement = document.createElement('h4');
    messageElement.textContent = text;
    messageElement.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
    messageElement.style.padding = '20px';
    messageElement.style.borderRadius = '10px';
    messageElement.style.backgroundColor = backgroundColor;
    messageElement.style.color = textColor;
    messageElement.style.position = 'fixed';
    messageElement.style.top = '50%';
    messageElement.style.left = '50%';
    messageElement.style.transform = 'translate(-50%, -50%)';

    return messageElement;
}

// Your existing code...

// Event listeners for sell buttons to display a modal
const sellButtons = document.querySelectorAll('.wannasell');
const modalContainer = document.getElementById('sellConfirmationModal');
const productNameElement = document.getElementById('productName');
const modalConfirmationButton = document.querySelector('.modal-confirmation');
const modalCancelButton = document.querySelector('.modal-cancel');

// Event listener for each sell button to show the modal
sellButtons.forEach(button => {
    button.addEventListener('click', function () {
        const productName = this.getAttribute('data-product-name');
        productNameElement.textContent = productName;
        showModal();
    });
});

// Event listeners for modal buttons
modalConfirmationButton.addEventListener('click', proceedWithSale);
modalCancelButton.addEventListener('click', cancelSale);

// Function to show the modal
function showModal() {
    modalContainer.style.display = 'flex';
}

// Function to hide the modal
function hideModal() {
    modalContainer.style.display = 'none';
}

// Function to proceed with the sale after confirming in the modal
function proceedWithSale() {
    hideModal();
    const productName = productNameElement.textContent;

    // Find the corresponding table row for the product
    const productRow = document.querySelector(`tr:has([data-product-name="${productName}"])`);

    if (productRow) {
        const productPrice = productRow.querySelector('td:nth-child(3)').textContent;

        // Function to send sale data to the server
        function makeSale(productName, productPrice, username) {
            const saleData = {
                'product_name': productName,
                'product_price': productPrice,
                'username': username, // Include the username in the data
            };

            // Send the sale data to the server using WebSocket
            socket.send(JSON.stringify({
                'type': 'record_sale',
                'sale_data': saleData,
            }));
        }

        // Call the makeSale function with relevant data
        makeSale(productName, productPrice, username);

        // Additional code if needed for successful sale confirmation
    } else {
        console.error('Product not found in the table');
    }
}

// Function to cancel the sale and hide the modal
function cancelSale() {
    hideModal();
}

// Search functionality
const searchInput = document.getElementById('searchInput');

// Event listener for the search input
searchInput.addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();

    // Loop through each table row in the tbody
    document.querySelectorAll('tbody tr').forEach(row => {
        const productName = row.querySelector('td:nth-child(2)').textContent.toLowerCase();

        // Check if the product name contains the search term
        if (productName.includes(searchTerm)) {
            row.style.display = ''; // Show the row
        } else {
            row.style.display = 'none'; // Hide the row
        }
    });
});
