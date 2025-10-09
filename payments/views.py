from pyexpat.errors import messages
from django.shortcuts import redirect, render

# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from groups.models import Group
from users.decorators import role_required
from django.utils.decorators import method_decorator
from .models import Payment, PaymentDate
from .forms import PaymentForm

# @method_decorator(role_required(['admin', 'accountant']), name='dispatch')
class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('student', 'group')
        student_id = self.request.GET.get('student')
        group_id = self.request.GET.get('group')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if group_id:
            queryset = queryset.filter(group_id=group_id)
            
        return queryset

# @method_decorator(role_required(['admin', 'accountant']), name='dispatch')
def payment_create(request):
    """
    Добавление нового платежа
    """
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
     
            return redirect(reverse('payment_list'))
    else:
        form = PaymentForm()

    return render(request, 'payments/payment_form.html', {'form': form})


# @method_decorator(role_required(['admin', 'accountant']), name='dispatch')
class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payment_list')

# @method_decorator(role_required(['admin', 'accountant', 'curator']), name='dispatch')
class StudentPaymentHistoryView(LoginRequiredMixin, ListView):
    """История платежей конкретного студента"""
    model = Payment
    template_name = 'payments/student_payment_history.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Payment.objects.filter(
            student_id=student_id
        ).select_related('group').order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from students.models import Student
        context['student'] = Student.objects.get(id=self.kwargs['student_id'])
        return context

# @method_decorator(role_required(['admin', 'accountant', 'curator']), name='dispatch')
class GroupPaymentStatusView(LoginRequiredMixin, DetailView):
    """Статус оплаты по группе"""
    model = Group
    template_name = 'payments/group_payment_status.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все даты оплат для этой группы
        context['payment_dates'] = PaymentDate.objects.filter(
            group=self.object
        ).select_related('student').order_by('student__full_name', 'month_number')
        return context