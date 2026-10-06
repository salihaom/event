from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'budget', 'location', 'event_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your event requirements...'}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={'placeholder': 'Enter your budget in INR'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, State'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Annual Company Gala 2025'}),
        }

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget and budget <= 0:
            raise forms.ValidationError('Budget must be a positive number.')
        return budget
