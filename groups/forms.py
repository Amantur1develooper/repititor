# groups/forms.py
from django import forms
from .models import Group, Enrollment

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'start_date', 'curator', 'is_active','lessons_per_month']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'curator': forms.Select(attrs={'class': 'form-control'}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'group', 'enrolled_from']
        widgets = {
            'enrolled_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }