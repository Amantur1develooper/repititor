from django import forms

from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'phone', 'phone_parent', 'parent_guardian', 'notes', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем Bootstrap-класс для всех полей
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Настраиваем виджет для заметок
        self.fields['notes'].widget = forms.Textarea(
            attrs={'rows': 3, 'class': 'form-control'}
        )
