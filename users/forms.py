from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import TemporaryMemory

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['first_name','last_name', 'username']
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
  
class EntryForm(forms.ModelForm):
    full_phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        help_text="Use international format +251..., +86..."
    )

    class Meta:
        model = TemporaryMemory
        fields = ['phone']

