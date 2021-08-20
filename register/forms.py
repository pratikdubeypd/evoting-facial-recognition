from django import forms
from django.contrib.auth.forms import PasswordResetForm

# overwriting django password reset form
class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(
        label='Email address', 
        widget=forms.EmailInput(attrs={
            'class': 'form-control my-2',
            'placeholder': 'Enter your registered email',
            'type': 'email',
            'name': 'email'
        }))