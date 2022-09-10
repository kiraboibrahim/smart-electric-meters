from django import forms

import meter_category.models as meter_category_models


class AddMeterCategoryForm(forms.ModelForm):

    class Meta:
        model = meter_category_models.MeterCategory
        fields = "__all__"

