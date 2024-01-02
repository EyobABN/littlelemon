from django.shortcuts import render
from .forms import BookingForm
from LittleLemonAPI.models import MenuItem, Booking
from django.core import serializers


# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def menu(request):    
    menu = MenuItem.objects.all()
    return render(request, 'menu.html', {"menu": menu})

def display_menu_item(request, pk=None):
    if pk:
        menu_item = MenuItem.objects.get(pk=pk)
    else:
        menu_item = ''
    return render(request, "menu_item.html", {"menu_item": menu_item})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            print(form)
    context = {'form':form}
    return render(request, 'book.html', context)

def reservations(request):
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html',{"bookings":booking_json})
