from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import TemporaryMemory

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    class Meta:
        model = User
        fields = ['first_name','last_name', 'username','email', 'password1', 'password2']
  
class EntryForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = TemporaryMemory
        fields = ['email']

