# students/forms.py
from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'phone', 
                 'parent_guardian', 'notes', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS-классы для стилизации
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Кастомные виджеты для лучшего UX
        self.fields['birth_date'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
        self.fields['notes'].widget = forms.Textarea(
            attrs={'rows': 3, 'class': 'form-control'}
        )