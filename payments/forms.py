from django import forms
from .models import Payment
# forms.py
from django import forms
from .models import Payment
from django.utils import timezone

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'student', 
            'group', 
            'date', 
            'payment_month', 
            'amount', 
            'months_count', 
            'notes'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_month': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'months_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # фильтруем только активных студентов
        self.fields['student'].queryset = self.fields['student'].queryset.filter(
            status__in=['active', 'debt']
        )

        # если дата не выбрана — ставим сегодняшнюю
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()

        # если месяц оплаты не выбран — ставим текущий месяц
        if not self.initial.get('payment_month'):
            today = timezone.now().date()
            self.initial['payment_month'] = today.replace(day=1)

    def clean_payment_month(self):
        """
        Приводим payment_month к первому числу выбранного месяца.
        """
        payment_month = self.cleaned_data['payment_month']
        if payment_month:
            payment_month = payment_month.replace(day=1)
        return payment_month
