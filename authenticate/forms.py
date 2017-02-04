from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=5,
        max_length=32)
