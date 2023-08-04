from django import forms


class PasswordInput(forms.PasswordInput):
    def __init__(self, *args, attrs=None, **kwargs):
        attrs = attrs or {}
        attrs["data-toggle"] = "password"
        super().__init__(*args, attrs=attrs, **kwargs)

    class Media:
        css = {
            "all": [
                "core/libs/bootstrap-password-toggle/css/password-toggle.css"
            ]
        }
        js = [
            "https://unpkg.com/bootstrap-show-password@1.2.1/dist/bootstrap-show-password.min.js"
        ]


class DateInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs") or {}
        attrs["type"] = "date"
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)
