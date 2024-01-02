from django.contrib import admin
from .models import Order, OrderItem, Cart, MenuItem, Category, Booking

# Register your models here.
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Booking)
