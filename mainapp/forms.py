from django import forms
from .models import TravelInfo, UserProfile
import pycountry
from django.utils import timezone
from django.contrib.auth.models import User
COUNTRY_CHOICES = sorted([(country.alpha_2, country.name) for country in pycountry.countries], key=lambda x: x[1])

class TravelFormCreate(forms.ModelForm):
    #name = forms.CharField(max_length=50)
    departure_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="From")
    destination_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="To")
    departure_date = forms.DateField(label='Departure Date',widget=forms.DateInput(attrs={'type': 'date'}))
    #max_weight = forms.IntegerField()
    note = forms.CharField(max_length=100)
    class Meta:
        model = TravelInfo
        fields = ['departure_country','destination_country','departure_date','max_weight','note']
        widgets = {
            'max_weight': forms.NumberInput(attrs={
                'type':'range',
                'min':'1',
                'max':'60',
                'step':'1',
                'oninput':'this.nextElementSibling.value = this.value'
            })
            }
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name','profile_picture','user_name','bio']

class SearchForm(forms.ModelForm):
    departure_country = forms.ChoiceField(choices=COUNTRY_CHOICES, initial="Afghanistan", label="From", required=True)
    destination_country = forms.ChoiceField(choices=COUNTRY_CHOICES,initial="Afghanistan", label="To", required=True)
    departure_date = forms.DateField(required=True, label='Departure Date',widget=forms.DateInput(attrs={'type': 'date','value':'Y-M-d'}))
    #max_weight = forms.IntegerField()
    class Meta:
        model = TravelInfo
        fields = ['departure_country','destination_country','departure_date','max_weight']
        widgets = {
            'max_weight': forms.NumberInput(attrs={
                'type':'range',
                'min':'1',
                'max':'60',
                'step':'1',
                'oninput':'this.nextElementSibling.value = this.value'
            })
        }

class SearchUsers(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by username...',
            'class': 'form-control'
        })
    )

class EditProfileForm(forms.ModelForm):
    # Fields from User model
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    # Phone is shown but not editable here
    phone = forms.CharField(required=False, disabled=True)

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone'].initial = user.userprofile.phone
            print (user.userprofile.phone)
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user_name  # your OneToOneField to User

        # Save User fields
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        if commit:
            user.save()
            profile.save()

        return profile

class EditPostForm(forms.ModelForm):
    departure_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="From")
    destination_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="To")
    departure_date = forms.DateField(label='Departure Date',widget=forms.DateInput(attrs={'type': 'date'}))
    note = forms.CharField(max_length=100)
    class Meta:
        model = TravelInfo
        fields = ['departure_country', 'destination_country','departure_date','max_weight','note']
        widgets = {
            'max_weight': forms.NumberInput(attrs={
                'type':'range',
                'min':'1',
                'max':'60',
                'step':'1',
                'oninput':'this.nextElementSibling.value = this.value'
            })
            }