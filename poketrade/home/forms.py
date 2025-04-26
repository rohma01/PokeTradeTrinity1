from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe

class CustomErrorList(forms.utils.ErrorList):
    def as_ul(self):
        return mark_safe(''.join([f'<li class="text-red-500">{e}</li>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']