from django.forms import ModelForm
from .models import Meter


class CreateMeterForm(ModelForm):
    class Meta:
        model = Meter
        fields = __all__
        exclude = ["manager"]
