from django import forms
from .models import Payment



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'date', 'amount', 'group', 'payment_month_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'payment_month_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
        