from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from rest_framework import generics, permissions, status
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer
from .permissions import IsManager, IsDeliveryCrew
from rest_framework.response import Response

# Create your views here.
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # permission_classes = [permissions.IsAuthenticated, IsManager]
    search_fields = ['title', 'category__title']

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow any authenticated user for GET requests
            return [permissions.IsAuthenticated()]
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
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsManager()]
        else:
            return super().get_permissions()

class ManagerUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        # Get Manager record from Group model
        manager_group = Group.objects.get(name='Manager')
        return manager_group.user_set.all()
    
    def perform_create(self, serializer):
        # Fetch the user by username from the request data
        username = self.request.data.get('username')
        user = get_object_or_404(User, username=username)

        # Add the user to the 'Manager' group
        manager_group = Group.objects.get(name='Manager')
        manager_group.user_set.add(user)

        self.response = Response({"detail": "User added to Manager group successfully"}, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        self.perform_create(serializer=self.get_serializer(data=request.data))

        # Return a successful response
        return self.response

class SingleManagerUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        # Get Manager record from Group model
        manager_group = Group.objects.get(name='Manager')
        return manager_group.user_set.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        manager_group = Group.objects.get(name='Manager')

        # Remove the user from the 'Manager' group
        manager_group.user_set.remove(instance)

        return Response({"detail": "User removed from Manager group successfully"}, status=status.HTTP_200_OK)

class DeliveryCrewUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        # Get 'Delivery crew' record from Group model
        manager_group = Group.objects.get(name='Delivery crew')
        return manager_group.user_set.all()
    
    def perform_create(self, serializer):
        # Fetch the user by username from the request data
        username = self.request.data.get('username')
        user = get_object_or_404(User, username=username)

        # Add the user to the 'Delivery crew' group
        manager_group = Group.objects.get(name='Delivery crew')
        manager_group.user_set.add(user)

        self.response = Response({"detail": "User added to Delivery crew group successfully"}, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        self.perform_create(serializer=self.get_serializer(data=request.data))

        # Return a successful response
        return self.response


class SingleDeliveryCrewUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        # Get Delivery crew record from Group model
        manager_group = Group.objects.get(name='Delivery crew')
        return manager_group.user_set.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        manager_group = Group.objects.get(name='Delivery crew')

        # Remove the user from the 'Delivery crew' group
        manager_group.user_set.remove(instance)

        return Response({"detail": "User removed from Delivery crew group successfully"}, status=status.HTTP_200_OK)
