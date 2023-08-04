from django import forms


class Select2Field(forms.ChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = ()  # Defer the loading of choices and lazily provide as the user types in the field
        super().__init__(*args, **kwargs)
