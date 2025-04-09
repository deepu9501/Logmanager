from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users based on the custom User model.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')  # यहां आप अन्य फील्ड्स भी शामिल कर सकते हैं


class UserProfileForm(forms.ModelForm):
    """
    A form for updating user profile information.
    """
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    notification_email = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    notification_sms = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'department', 'phone', 'notification_email', 'notification_sms') 