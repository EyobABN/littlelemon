from django.forms import ModelForm
from LittleLemonAPI.models import Booking


# Code added for loading form data on the Booking page
class BookingForm(ModelForm):
    pass
    class Meta:
        model = Booking
        fields = "__all__"
