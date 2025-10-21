from pyexpat.errors import messages
from django.shortcuts import redirect, render

# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from students.models import Student
from groups.models import Enrollment, Group
from users.decorators import role_required
from django.utils.decorators import method_decorator
from .models import Payment, PaymentDate
from .forms import PaymentForm
from django.http import JsonResponse

def get_next_month_number(request):
    student_id = request.GET.get('student')
    group_id = request.GET.get('group')
    
    if student_id and group_id:
        try:
            enrollment = Enrollment.objects.get(student_id=student_id, group_id=group_id)
            return JsonResponse({'next_month': enrollment.get_next_personal_month()})
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': 'Enrollment not found'}, status=404)
    
    return JsonResponse({'error': 'Missing parameters'}, status=400)
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
from django.http import JsonResponse
from django.db.models import Q
def d(request):
    return render(request, 'payments/a.html')
def search_students(request):
    """API для поиска студентов"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    students = Student.objects.filter(
        Q(full_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(phone_parent__icontains=query)
    )[:20]
    
    results = [{
        'id': student.id,
        'text': f"{student.full_name} ({student.phone})"
    } for student in students]
    
    return JsonResponse({'results': results})
# @method_decorator(role_required(['admin', 'accountant']), name='dispatch')
# def payment_create(request):
#     """
#     Добавление нового платежа
#     """
#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             form.save()
     
#             return redirect(reverse('payment_list'))
#     else:
#         form = PaymentForm()

#     return render(request, 'payments/payment_form.html', {'form': form})


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
    
def payment_create(request):
    """
    Добавление нового платежа с улучшенным поиском студентов
    """
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
           
         
            payment = form.save(commit=False)
         
            student = payment.student
            group = payment.group
            
            try:
                enrollment = Enrollment.objects.get(student=student, group=group)
                next_personal_month = enrollment.get_next_personal_month()
                payment.payment_month_number = next_personal_month
                
                print(f"DEBUG: Создаем платеж для студента {student}, месяца {next_personal_month}")
                
                payment.save()
                # messages.success(request, f'Платеж для успешно добавлен!')
                return redirect(reverse('payment_list'))
                
            except Enrollment.DoesNotExist:
                form.add_error(None, f'Студент {student.get_full_name()} не зачислен в группу {group.name}')
    else:
        student_id = request.GET.get('student')
        group_id = request.GET.get('group')
        
        
        initial_data = {}
        if student_id and group_id:
            try:
                enrollment = Enrollment.objects.get(student_id=student_id, group_id=group_id)
                initial_data['payment_month_number'] = enrollment.get_next_personal_month()
                print(f"DEBUG: Предустановленный месяц: {initial_data['payment_month_number']}")
            except Enrollment.DoesNotExist:
                messages.warning(request, 'Студент не найден в указанной группе')

        form = PaymentForm(initial=initial_data)

    return render(request, 'payments/payment_form.html', {'form': form})
# def payment_create(request):
#     """
#     Добавление нового платежа - ОБНОВЛЕННАЯ ВЕРСИЯ
#     """
#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             # Получаем объект платежа перед сохранением
#             payment = form.save(commit=False)
            
#             # Автоматически устанавливаем номер месяца на основе студента и группы
#             student = payment.student
#             group = payment.group
            
#             # Находим зачисление студента
#             enrollment = Enrollment.objects.get(student=student, group=group)
#             next_personal_month = enrollment.get_next_personal_month()
            
#             # Устанавливаем номер месяца
#             payment.payment_month_number = next_personal_month
            
#             print(f"DEBUG: Создаем платеж для месяца {next_personal_month}")
            
#             payment.save()
#             return redirect(reverse('payment_list'))
#     else:
#         student_id = request.GET.get('student')
#         group_id = request.GET.get('group')
        
#         # Предзаполняем номер месяца
#         initial_data = {}
#         if student_id and group_id:
#             try:
#                 enrollment = Enrollment.objects.get(student_id=student_id, group_id=group_id)
#                 next_personal_month = enrollment.get_next_personal_month()
#                 initial_data['payment_month_number'] = next_personal_month
#                 print(f"DEBUG: Предустановленный месяц: {next_personal_month}")
#             except Enrollment.DoesNotExist:
#                 pass
        
#         form = PaymentForm(initial=initial_data)

#     return render(request, 'payments/payment_form.html', {'form': form})

# views.py
from django.http import JsonResponse
from django.db.models import Q

def student_search_api(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        students = Student.objects.filter(
            Q(full_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(phone_parent__icontains=query) |
            Q(parent_guardian__icontains=query)
        )[:10]  # Ограничиваем результаты
        
        results = [{
            'id': student.id,
            'text': f"{student.full_name} | 📞 {student.phone or 'нет телефона'}"
        } for student in students]
        
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})