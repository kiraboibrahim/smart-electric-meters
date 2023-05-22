from django import forms

import meter_categories.models as meter_category_models


class AddMeterCategoryForm(forms.ModelForm):

    class Meta:
        model = meter_category_models.MeterCategory
        exclude = ("is_default",)

