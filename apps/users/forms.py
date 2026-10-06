from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, ManagerProfile


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'city', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ManagerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False)
    services_offered = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. Catering, Photography, Decoration'}),
        help_text="Enter services separated by commas"
    )
    price_min = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    price_max = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    location = forms.CharField(max_length=200)
    experience_years = forms.IntegerField(min_value=0, initial=0)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'city', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'manager'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            ManagerProfile.objects.create(
                user=user,
                bio=self.cleaned_data.get('bio', ''),
                services_offered=self.cleaned_data['services_offered'],
                price_min=self.cleaned_data['price_min'],
                price_max=self.cleaned_data['price_max'],
                location=self.cleaned_data['location'],
                experience_years=self.cleaned_data['experience_years'],
            )
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ManagerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        fields = ['bio', 'services_offered', 'price_min', 'price_max', 'location', 'experience_years', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'services_offered': forms.Textarea(attrs={'rows': 3}),
        }
