from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.CategoryView.as_view(), name='CategoryView'),
    path('menu-items', views.MenuItemsView.as_view(), name='MenuItemsView'),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view(), name='SingleMenuItemView'),
    path('groups/manager/users', views.ManagerUsersView.as_view(), name='ManagerUsersView'),
    path('groups/manager/users/<int:pk>', views.SingleManagerUserView.as_view(), name='SingleManagerUserView'),
    path('groups/delivery-crew/users', views.DeliveryCrewUsersView.as_view(), name='DeliveryCrewUsersView'),
    path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewUserView.as_view(), name='SingleDeliveryCrewUserView'),
    path('cart/menu-items', views.CartView.as_view(), name='CartView'),
    path('orders', views.OrdersView.as_view(), name='OrdersView'),
    path('orders/<int:pk>', views.SingeOrderView.as_view(), name='SingleOrderView')
]