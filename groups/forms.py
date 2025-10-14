# groups/forms.py
from django import forms
from .models import Group, Enrollment

from django import forms
from .models import Group, Student
from django.contrib.auth.models import User

class GroupForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Ученики'
    )
    curator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Куратор'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата начала 1-го месяца обучения'
    )

    class Meta:
        model = Group
        fields = [
            'name',
            'students',
            'start_date',
            'curator',
            'is_active',
            'lessons_per_month',
            'monthly_price',
        ]


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'group', 'enrolled_from']
        widgets = {
            'enrolled_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }