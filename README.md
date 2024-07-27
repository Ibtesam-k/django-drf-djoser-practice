# Restaurant Management API

The Restaurant Management API is a backend application that provides a RESTful API for managing the operations of a restaurant, including user management, menu items, carts, orders, and user groups.

## Features

- **User Management**: 
  - Read, create, update, and delete users using Djoser.
  - **Base URL**: `http://127.0.0.1:8000/auth`

- **User Groups Management**: 
  - Add or remove users from groups such as delivery crew, managers, and customers.
  - **Base URL**: `http://127.0.0.1:8000/api/groups`

- **Menu Items Management**: 
  - Read, create, update, and delete menu items.
  - **Base URL**: `http://127.0.0.1:8000/api/menu-items`

- **Cart Management**: 
  - Add items to the cart, retrieve cart items, and clear the cart.
  - **Base URL**: `http://127.0.0.1:8000/api/cart/menu-items`

- **Orders Management**: 
  - Place orders, read orders as a customer, manage orders as a manager, assign orders to delivery crew, and update order status.
  - **Base URL**: `http://127.0.0.1:8000/api/orders`


## Usage Notes

- A list of credentials for users in the database is available in a file named `users.txt` in the project base folder.
- A categorized endpoints collection exported from the Insomnia app is available as a JSON file named `LittleLemonAPI_Insomnia.json` in the project base folder. 
  - This JSON file can be easily imported into Insomnia for easy access to endpoints and testing.
  - The endpoints include preset data in fields like auth and body according to request type. It may contain tokens for authorization and/or form data to post or update objects. You can modify this data to test different scenarios.
  - When browsing menu items or orders, remember to change the page number in the request URL to retrieve all available data.

## Getting Started

1. Clone the repository.
2. Install the required dependencies.
3. Run the server using the command:
   ```bash
   python manage.py runserver
4. Access the API at the specified base URLs.