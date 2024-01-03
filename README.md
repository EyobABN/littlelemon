# Django-LittleLemon-API-Advanced
Fully functional RESTful API project for the Little Lemon restaurant. Client application developers can use the APIs to develop web and mobile applications. Authentication, authorization, ordering, searching, pagination and throttling implemented. People with different roles will be able to browse, add and edit menu items, place orders, browse orders, assign delivery crew to orders and finally deliver the orders. The `restaurant` app within the django project is a simple UI interface implemented using Django templates.

## Getting Started

#### Clone the Repository
```bash
git clone https://github.com/EyobABN/littlelemon.git
cd littlelemon
```

#### Install dependencies with Pipenv
```bash
pipenv install
```

#### Activate the Virtual Environment
```bash
pipenv shell
```

#### Database Migrations
```bash
python manage.py migrate
```

#### Run the Development Server
```bash
python manage.py runserver
```

#### Access the Application
Open your browser and go to http://127.0.0.1:8000

## User Groups:
1. `Manager` - managers are added to this group
2. `Delivery crew` - Delivery crew are added to this group
- Registered users who are not members of either group are considered customers.

## Features:

1. The admin can assign users to the manager group
2. An admin with an admin token can access the manager group
3. The admin can add menu items
4. The admin can add categories
5. Managers can log in
6. Managers can update the item of the day
7. Managers can assign users to the delivery crew
8. Managers can assign orders to the delivery crew
9. The delivery crew can access orders assigned to them
10. The delivery crew can update an order as delivered
11. Customers can register
12. Customers can log in using their username and password and get access tokens
13. Customers can browse all categories 
14. Customers can browse all the menu items at once
15. Customers can browse menu items by category
16. Customers can paginate menu items
17. Customers can sort menu items by price
18. Customers can add menu items to the cart
19. Customers can access previously added items in the cart
20. Customers can place orders
21. Customers can browse their own orders


## API Endpoints

### User Registration and Token Generation endpoints:

| Endpoint | Role | Method | Purpose |
|----------|------|--------|---------|
| /auth/users/ | No role required | `POST` | Creates a new user with username, email and password |
| /auth/users/me/ | Anyone with a valid user token | `GET` | Displays only the current user |
| /auth/token/login/ | Anyone with a valid username and password | `POST` | Generates access tokens that can be used in other API calls in this project |

### Menu Item endpoints:

| Endpoint | Role | Method | Purpose |
|----------|------|--------|---------|
| /api/menu-items | Customer, Delivery crew | `GET` | Lists all menu items and returns `200 - OK` |
| /api/menu-items | Customer, Delivery crew | `POST`, `PUT`, `PATCH`, `DELETE` | Denies access and returns `403 - Forbidden` |
| /api/menu-items/{menuItem} | Customer, Delivery crew | `GET` | Lists a single menu item |
| /api/menu-items/{menuItem} | Customer, Delivery crew | `POST`, `PUT`, `PATCH`, `DELETE` | Returns `403 - Forbidden` |
| /api/menu-items | Manager | `GET` | Lists all menu items |
| /api/menu-items | Manager | `POST` | Creates a new menu item and returns `201 - Created` |
| /api/menu-items/{menuItem} | Manager | `GET` | Lists a single menu item |
| /api/menu-items/{menuItem} | Manager | `PUT`, `PATCH` | Updates single menu item |
| /api/menu-items/{menuItem} | Manager | `DELETE` | Deletes menu item |

### User group management endpoints:

| Endpoint | Role | Method | Purpose |
|----------|------|--------|---------|
| /api/groups/manager/users | Manager | `GET` | Returns all managers |
| /api/groups/manager/users | Manager | `POST` | Assigns the user in the payload to the `Manager` group and returns `201 - Created` |
| /api/groups/manager/users/{userId} | Manager | `DELETE` | Removes this user from the manager group and returns `200 - Ok` upon success or `404 - Not found` if the user does not belong to the `Manager` group |
| /api/groups/delivery-crew/users | Manager | `GET` | Returns all delivery crew |
| /api/groups/delivery-crew/users | Manager | `POST` | Assigns the user in the payload to the `Delivery crew` group and returns `201 - Created` |
| /api/groups/delivery-crew/users/{userId} | Manager | `DELETE` | Removes this user from the `Delivery crew` group and returns `200 - Ok` success or `404 - Not found` if the user does not belong to the `Delivery crew` group |

### Cart management endpoints:

| Endpoint | Role | Method | Purpose |
|----------|------|--------|---------|
| /api/cart/menu-items | Customer | `GET` | Returns current user's cart items |
| /api/cart/menu-items | Customer | `POST` | Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items |
| /api/cart/menu-items | Customer | `DELETE` | Deletes all menu items in the user's cart |

### Order management endpoints:

| Endpoint | Role | Method | Purpose |
|----------|------|--------|---------|
| /api/orders | Customer | `GET` | Returns all order items created by the current user |
| /api/orders | Customer | `POST` | Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user. |
| /api/orders/{orderId} | Customer | `GET` | Returns all items for this order id. If the order with this order id doesn't belong to the current user, returns `403 - Forbidden`  |
| /api/orders | Manager | `GET` | Returns all orders belonging to any customer |
| /api/orders/{orderId} | Customer | `PUT`, `PATCH` | Updates the order. A manager can use this endpoint to set a delivery crew to this order, and also update the order status to 0 or 1. If a delivery crew member is assigned to this order and the status = 0, it means the order has been dispatched for delivery but has not yet been delivered. If a delivery crew member is assigned to this order and the status = 1, it means the order has been delivered. |
| /api/orders/{orderId} | Manager | `DELETE` | Deletes this order |
| /api/orders | Delivery crew | `GET` | Returns all orders with assigned to this delivery crew member |
| /api/orders/{orderId} | Delivery crew | `PATCH` | A delivery crew can use this endpoint to update the order status to 0 or 1. The delivery crew is not able to update anything else in this order. |

## Ordering

The `/api/menu-items` and `/api/orders` endpoints support ordering by the following fields:

#### Menu Items ordering fields:
- `title`: order alphabetically by the name of the menu item
- `price`: order numerically by the price of the menu item

#### Orders ordering fields:
- `date`: order by date the order was made on
- `total`: order by the total price of the order
  
To specify the order in which the responses should be presented, one or more of these fields can be included in the `ordering` query parameter.

To sort in ascending order, include the desired fields directly. To sort in descending order, prepend the field with `-`. For instance, to order menu items by category in ascending order and then by price in descending order, use the following query:

```plaintext
/api/menu-items?ordering=category,-price
```

## Searching

The `/api/menu-items` and `/api/orders` endpoints support searching in the following fields:

#### Menu Items Search Fields:

- `title`: Search by the name of the menu item.
- `category__title`: Search by the name of the category ('main', 'appetizer', 'dessert') to which the menu item belongs.

#### Orders Search Fields:

- `user__username`: Search by the username of the user who placed the order.
- `delivery_crew__username`: Search by the username of the delivery crew responsible for the order.

To perform a search, use the `search` query parameter in the API request. For example, to find menu items with the word "Burger" in their title, use:

```plaintext
/api/menu-items?search=pasta
```

## Pagination
The `/api/menu-items` and `/api/orders` endpoints also support pagination. Users can specify the number of items that should be included per page by setting the `page_size` query parameter, while `page` is used to specify which page to return. For example, to receive page number 2 at 5 menu items per page, the following query can be used:
```plaintext
/api/menu-items?page=2&page_size=5
```

## Throttling
A limit has been set on the number of requests that can be made to the API in a given time span.

## UI Endpoints

* / - homepage
* /about - Information about the Little Lemon restaurant
* /menu - Displays the menu items currently available
* /book/ - Allows customers to make a reservation at the restaurant


