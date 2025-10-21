from django import forms
from .models import Payment, Student

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'date', 'amount', 'group', 'payment_month_number', 'notes']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control',  # УБРАЛ select2-search - будем добавлять через JS
                'data-placeholder': 'Начните вводить ФИО для поиска...'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01'
            }),
            'group': forms.Select(attrs={
                'class': 'form-control'
            }),
            'payment_month_number': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Улучшаем отображение студентов в выпадающем списке
        self.fields['student'].queryset = Student.objects.all()
        self.fields['student'].label_from_instance = lambda obj: f"{obj.full_name} ({obj.phone})"