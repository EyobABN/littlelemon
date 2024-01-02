from datetime import date
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, IsDeliveryCrew
from rest_framework.response import Response

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category__title']
    ordering_fields = ['title', 'price', 'featured', 'category__title']

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow anyone for GET requests
            return []
        elif self.request.method == 'POST':
            # Allow only managers for POST requests
            return [permissions.IsAuthenticated(), IsManager()]
        else:
            return super().get_permissions()

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsManager()]
        else:
            return super().get_permissions()

class GroupUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]
    group_name = None  # This should be overridden in subclasses

    def get_queryset(self):
        if self.group_name is None:
            raise NotImplementedError("Subclasses must define group_name")
        # Get group record from Group model
        group = Group.objects.get(name=self.group_name)
        return group.user_set.all()
    
    def perform_create(self, serializer):
        # Fetch the user by username from the request data
        username = self.request.data.get('username')
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name=self.group_name)
        except User.DoesNotExist:
            return Response({'detail': f"There is no user with username {username}"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'detail': f"Server configuration error: no group named {self.group_name}"}, status=status.HTTP_501_NOT_IMPLEMENTED)

        # Add the user to the group
        group.user_set.add(user)

        return Response({'detail': f"{username} added to {self.group_name} group successfully"}, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        return self.perform_create(serializer=self.get_serializer(data=request.data))

class SingleGroupUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]
    group_name = None  # This should be overridden in subclasses

    def get_queryset(self):
        if self.group_name is None:
            raise NotImplementedError("Subclasses must define group_name")
        # Get group record from Group model
        group = Group.objects.get(name=self.group_name)
        return group.user_set.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        group = Group.objects.get(name=self.group_name)

        # Remove the user from the group
        group.user_set.remove(instance)

        return Response({'detail': f"{instance.username} removed from {self.group_name} group successfully"}, status=status.HTTP_200_OK)

class ManagerUsersView(GroupUsersView):
    group_name = 'Manager'

class SingleManagerUserView(SingleGroupUserView):
    group_name = 'Manager'

class DeliveryCrewUsersView(GroupUsersView):
    group_name = 'Delivery crew'

class SingleDeliveryCrewUserView(SingleGroupUserView):
    group_name = 'Delivery crew'

class CartView(generics.CreateAPIView, generics.ListAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        menuitem_id = self.request.data.get('menuitem')
        quantity = self.request.data.get('quantity')

        if not menuitem_id or not quantity:
            raise serializers.ValidationError({'error': "menuitem and quantity are required"})

        menuitem = get_object_or_404(MenuItem, id=menuitem_id)
        unitprice = menuitem.price
        price = unitprice * int(quantity)

        serializer.save(user=self.request.user, menuitem=menuitem, quantity=quantity, unitprice=unitprice, price=price) # will raise IntegrityError if the same menu item is added twice

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response({'detail': "Cart items deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    search_fields = ['user__username', 'delivery_crew__username']
    ordering_fields = ['date', 'total', 'user', 'status', 'delivery_crew']
    
    def get_queryset(self):
        user = self.request.user
        groups = [group.name for group in user.groups.all()]
        is_manager = 'Manager' in groups
        is_delivery_crew = 'Delivery crew' in groups
        if is_manager:
            # Return orders belonging to all users
            return Order.objects.all()
        elif is_delivery_crew:
            # Return orders that were assigned to delivery crew user
            return Order.objects.filter(delivery_crew=user)
        else:
            # Return customer's own orders only
            return Order.objects.filter(user=user)
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        groups = [group.name for group in user.groups.all()]
        is_manager = 'Manager' in groups
        is_delivery_crew = 'Delivery crew' in groups
        # Check if user is customer
        if not (is_manager or is_delivery_crew):
            # Create order
            order_data = {
                'user': user.id,
                'delivery_crew': None,
                'status': 0,
                'total': 0,
                'date': date.today()
            }
            order_serializer = OrderSerializer(data=order_data)
            if order_serializer.is_valid():
                order = order_serializer.save()
                # Get cart items related to customer
                cart_items = Cart.objects.filter(user=user)
                # Add each cart item to an order item
                for cart_item in cart_items:
                    order_item_data = {
                        'order': order.id,
                        'menuitem': cart_item.menuitem.id,
                        'quantity': cart_item.quantity,
                        'unitprice': cart_item.unitprice,
                        'price': cart_item.price
                    }
                    order_item_serializer = OrderItemSerializer(data=order_item_data)
                    if order_item_serializer.is_valid():
                        order_item_serializer.save()
                        order.total += cart_item.price
                        order.save()
                    else:
                        return Response(order_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                # Delete cart item
                cart_items.delete()
                return Response({'detail': "Order created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': "Permission denied. Only customers can create orders"}, status=status.HTTP_403_FORBIDDEN)

class SingeOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        groups = [group.name for group in user.groups.all()]
        is_manager = 'Manager' in groups
        is_delivery_crew = 'Delivery crew' in groups
        if is_manager:
            return Order.objects.all()
        elif is_delivery_crew:
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)
    
    def get(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        groups = [group.name for group in user.groups.all()]
        is_customer = ('Manager' not in groups) and ('Delivery crew' not in groups)

        # check if the order belongs to the current user (for customers)
        if is_customer and order.user != request.user:
            return Response({'detail': "Permission denied. This order does not belong to the current user"}, status=status.HTTP_403_FORBIDDEN)
        
        order_items = OrderItem.objects.filter(order=order)
        serialized_order_items = OrderItemSerializer(order_items, many=True)
        return Response(serialized_order_items.data)
    
    def put(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        groups = [group.name for group in user.groups.all()]
        is_manager = 'Manager' in groups

        if not is_manager:
            return Response({'detail': "Permission denied. Only managers are allowed to make PUT requests."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        groups = [group.name for group in user.groups.all()]
        is_manager = 'Manager' in groups
        is_delivery_crew = 'Delivery crew' in groups

        # Make sure the customer is either a manager or delivery crew
        if not (is_manager or is_delivery_crew):
            return Response({'detail': "Permission denied. Customers are not allowed to edit orders."}, status=status.HTTP_403_FORBIDDEN)

        # Partially update the order
        # Delivery crew can only update the status of orders assigned to them
        if is_delivery_crew:
            if order.delivery_crew != request.user:
                return Response({'detail': "Permission denied. This order is not assigned to the current delivery crew member."}, status=status.HTTP_403_FORBIDDEN)
            if 'status' in request.data:
                status_value = request.data['status']
                if not isinstance(status_value, bool):
                    return Response({'detail': "Invalid value for 'status'. Must be a boolean value."}, status=status.HTTP_400_BAD_REQUEST)
                order.status = bool(status_value)
                order.save()

                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response({'detail': "Missing \'status\' field in the request"}, status=status.HTTP_400_BAD_REQUEST)
        

        # Managers can edit other fields too
        if is_manager:
            serializer = self.get_serializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                except ValidationError:
                    # assigned user is not in Delivery crew group
                    return Response({'detail': "User must belong to the 'Delivery crew' group"}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # Custom logic for handling DELETE requests
        order = self.get_object()
        user = request.user
        groups = [group.name for group in user.groups.all()]
        is_manager = 'Manager' in groups

        # Make sure the customer is a manager 
        if not is_manager:
            return Response({'detail': "Permission denied. Only managers are allowed to delete orders."}, status=status.HTTP_403_FORBIDDEN)

        # Your logic for deleting the order goes here
        order.delete()
        return Response({'detail': "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
