from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title

class MenuItem(models.Model):
    # title, price, featured, category
    title = models.CharField(max_length=255, db_index=True, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    description = models.CharField(max_length=1000, default='none')
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

class Cart(models.Model):
    # user, menuitem, quantity, unitprice, price
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unitprice = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('user', 'menuitem')

class DeliveryCrewManager(models.Manager):
    def clean_delivery_crew(self, user):
        # Ensure that the user belongs to the 'Delivery Crew' group
        if 'Delivery crew' not in [group.name for group in user.groups.all()]:
            raise ValidationError("User must belong to the 'Delivery crew' group.")

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew_user', null=True)
    status = models.BooleanField(db_index=True, default=False)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)

    objects = DeliveryCrewManager()

    def clean(self):
        # Check the user's group when saving the model
        if self.delivery_crew:
            Order.objects.clean_delivery_crew(self.delivery_crew)
    
    def save(self, *args, **kwargs):
        # Check the user's group when saving the model
        if self.delivery_crew:
            Order.objects.clean_delivery_crew(self.delivery_crew)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unitprice = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')

class Booking(models.Model):
   first_name = models.CharField(max_length=200)    
   last_name = models.CharField(max_length=200)
   guest_number = models.IntegerField()
   reservation_date = models.DateField()
   reservation_slot = models.SmallIntegerField()
   comment = models.CharField(max_length=1000)

   def __str__(self):
      return self.first_name + ' ' + self.last_name
