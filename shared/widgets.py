from django import forms


class PasswordInput(forms.PasswordInput):
    """
    https://unpkg.com/bootstrap-show-password@1.2.1/dist/bootstrap-show-password.min.js Depends on the data-toggle
    attribute to toggle password visibility
    """
    def __init__(self, *args, attrs=None, **kwargs):
        attrs = attrs or {}
        attrs["data-toggle"] = "password"
        super().__init__(*args, attrs=attrs, **kwargs)
