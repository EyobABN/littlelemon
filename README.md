# Django-LittleLemon-API-Advanced
Fully functioning API project for the Little Lemon restaurant so that the client application developers can use the APIs to develop web and mobile applications. People with different roles will be able to browse, add and edit menu items, place orders, browse orders, assign delivery crew to orders and finally deliver the orders.

Groups:
1. Manager: managers are added to this group
2. Delivery crew: Delivery crew are added to this group
   Registered users who are not members of either group are considered customers.

Capabilities:

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


API Endpoints:

---User Registration and Token Generation Endpoints:

•	/auth/users/
•	/auth/users/me/
•	/auth/token/login/

---Menu Item Endpoints:

•	/api/menu-items
•	/api/menu-items/{menuItem}
•	/api/menu-items
•	/api/menu-items/{menuItem}

---User group management endpoints:

•	/api/groups/manager/users
•	/api/groups/manager/users/{userId}
•	/api/groups/delivery-crew/users
•	/api/groups/delivery-crew/users/{userId}

---Cart management endpoints:

•	/api/cart/menu-items

---Order management endpoints:

•	/api/orders
•	/api/orders/{orderId}
