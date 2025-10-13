# groups/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from payments.models import Payment
from users.decorators import role_required
from django.utils.decorators import method_decorator
from .models import Enrollment, Group
from .forms import GroupForm
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from users.decorators import role_required
from django.utils.decorators import method_decorator
from .models import Group, Enrollment
from dateutil.relativedelta import relativedelta

# @method_decorator(role_required(['admin', 'curator']), name='dispatch')
class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'groups/group_list.html'
    context_object_name = 'groups'
    
    def get_queryset(self):
        queryset = Group.objects.all()
        curator = self.request.GET.get('curator')
        active = self.request.GET.get('active')
        
        if curator:
            queryset = queryset.filter(curator_id=curator)
        if active == 'true':
            queryset = queryset.filter(is_active=True)
        elif active == 'false':
            queryset = queryset.filter(is_active=False)
            
        return queryset.select_related('curator').prefetch_related('students')

# @method_decorator(role_required(['admin']), name='dispatch')
class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_form.html'
    success_url = reverse_lazy('group_list')
    
class GroupIncrementLessonView(LoginRequiredMixin, View):
    """View для увеличения счетчика занятий группы"""
    
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        
        # Увеличиваем счетчики посещений для всех студентов группы
        enrollments = Enrollment.objects.filter(group=group)
        for enrollment in enrollments:
            enrollment.increment_attendance()
        
        messages.success(
            request, 
            f'Занятие добавлено для всех студентов группы'
        )
        
        return redirect('group_detail', pk=group.pk)
# class GroupIncrementLessonView(LoginRequiredMixin, View):
#     """View для увеличения счетчика занятий и посещений"""
    
#     def post(self, request, pk):
#         group = get_object_or_404(Group, pk=pk)
        
#         # Увеличиваем общее количество занятий в группе
#         group.lessons_count += 1
#         group.save()
        
#         # Увеличиваем счетчики посещений для всех студентов группы
#         enrollments = Enrollment.objects.filter(group=group)
#         for enrollment in enrollments:
#             enrollment.increment_attendance()
        
#         # Проверяем, нужно ли проверять оплату
#         if group.should_check_payment():
#             messages.warning(
#                 request, 
#                 f'Группа завершила {group.lessons_count} занятий! Проверьте оплату за {group.get_next_month()} месяц.'
#             )
#         else:
#             messages.success(
#                 request, 
#                 f'Занятие добавлено. Всего проведено: {group.lessons_count}'
#             )
        
#         return redirect('group_detail', pk=group.pk)
# @method_decorator(role_required(['admin']), name='dispatch')
class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_form.html'
    success_url = reverse_lazy('group_list')

# @method_decorator(role_required(['admin', 'curator']), name='dispatch')
# groups/views.py
# groups/views.py
from django.db.models import Sum
from django.db.models import Sum
from payments.models import PaymentDate
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from payments.models import Payment
from django.db.models import Sum
class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object

        enrollments = group.enrollment_set.all().select_related('student')
        
        enrollments_with_payments = []
        
        for enrollment in enrollments:
            # Используем ПЕРСОНАЛЬНЫЙ следующий месяц студента
            next_personal_month = enrollment.get_next_personal_month()
            
            # Получаем статус оплаты за следующий персональный месяц
            payment_status = Payment.get_student_payment_status(
                enrollment.student,
                group,
                next_personal_month  # Важно: используем следующий персональный месяц
            )
            
            # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
            debug_info = {
                'student': enrollment.student.full_name,
                'personal_month': enrollment.get_personal_month(),
                'next_personal_month': next_personal_month,
                'lessons_attended': enrollment.lessons_attended,
                'payment_status': payment_status
            }
            print("DEBUG:", debug_info)  # Смотрите в консоли сервера
            
            enrollments_with_payments.append({
                'enrollment': enrollment,
                'payment_status': payment_status,
                'next_personal_month': next_personal_month,
                'should_check_payment': enrollment.should_check_personal_payment(),
                'progress_percent': enrollment.get_personal_progress_percent(),
                'debug_info': debug_info  # Для отладки в шаблоне
            })

        # Расчет статистики
        total_count = len(enrollments_with_payments)
        paid_count = sum(1 for i in enrollments_with_payments if i['payment_status']['is_fully_paid'])
        partial_count = sum(1 for i in enrollments_with_payments if i['payment_status']['is_partially_paid'])
        completed_count = sum(1 for i in enrollments_with_payments if i['should_check_payment'])
        not_paid_count = sum(
            1 for i in enrollments_with_payments 
            if i['should_check_payment'] and not i['payment_status']['is_fully_paid']
        )

        context['enrollments_with_payments'] = enrollments_with_payments
        context['total_count'] = total_count
        context['paid_count'] = paid_count
        context['partial_count'] = partial_count
        context['completed_count'] = completed_count
        context['not_paid_count'] = not_paid_count

        return context
# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object

#         enrollments = group.enrollment_set.all().select_related('student')
        
        
        
      
#         enrollments_with_payments = []
        
#         for enrollment in enrollments:
#             next_personal_month = enrollment.get_next_personal_month()
#             payment_status = Payment.get_student_payment_status_by_month_number(
#                 enrollment.student,
#                 group,
#                 next_personal_month
#             )
            
#             enrollments_with_payments.append({
#                 'enrollment': enrollment,
#                 'payment_status': payment_status,
#                 'next_personal_month': next_personal_month,
#                 'should_check_payment': enrollment.should_check_personal_payment(),
#                 'progress_percent': enrollment.get_personal_progress_percent()
#             })

#         total_count = len(enrollments_with_payments)
#         paid_count = sum(1 for i in enrollments_with_payments if i['payment_status']['is_fully_paid'])
#         partial_count = sum(1 for i in enrollments_with_payments if i['payment_status']['is_partially_paid'])
#         completed_count = sum(1 for i in enrollments_with_payments if i['should_check_payment'])
#         not_paid_count = sum(
#             1 for i in enrollments_with_payments 
#             if i['should_check_payment'] and not i['payment_status']['is_fully_paid']
#         )

#         context['enrollments_with_payments'] = enrollments_with_payments
#         context['total_count'] = total_count
#         context['paid_count'] = paid_count
#         context['partial_count'] = partial_count
#         context['completed_count'] = completed_count
#         context['not_paid_count'] = not_paid_count

#         return context

# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object

#         enrollments = group.enrollment_set.all().select_related('student')

#         enrollments_with_payments = []
#         for enrollment in enrollments:
#             next_personal_month = enrollment.get_next_personal_month()
#             payment_status = Payment.get_student_payment_status_by_month_number(
#                 enrollment.student,
#                 group,
#                 next_personal_month
#             )
#             enrollments_with_payments.append({
#                 'enrollment': enrollment,
#                 'payment_status': payment_status,
#                 'next_personal_month': next_personal_month,
#                 'should_check_payment': enrollment.should_check_personal_payment(),
#                 'progress_percent': enrollment.get_personal_progress_percent()
#             })

#         total_count = len(enrollments_with_payments)
#         paid_count = sum(1 for i in enrollments_with_payments if i['payment_status']['is_fully_paid'])
#         partial_count = sum(1 for i in enrollments_with_payments if i['payment_status']['is_partially_paid'])
#         context['enrollments_with_payments'] = enrollments_with_payments
#         context['total_count'] = total_count
#         context['paid_count'] = paid_count
#         context['partial_count'] = partial_count

#         return context

# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object

#         # Получаем все зачисления студентов
#         enrollments = group.enrollment_set.all().select_related('student')

#         # Формируем список с информацией о платежах
#         enrollments_with_payments = []
#         for enrollment in enrollments:
#             next_personal_month = enrollment.get_next_personal_month()
#             payment_status = Payment.get_student_payment_status_by_month_number(
#                 enrollment.student,
#                 group,
#                 next_personal_month
#             )

#             enrollments_with_payments.append({
#                 'enrollment': enrollment,
#                 'payment_status': payment_status,
#                 'next_personal_month': next_personal_month,
#                 'should_check_payment': enrollment.should_check_personal_payment(),
#                 'progress_percent': enrollment.get_personal_progress_percent()
#             })

#         # ✅ Подсчёт количества оплативших и общего числа
#         total_count = len(enrollments_with_payments)
#         paid_count = sum(
#             1 for item in enrollments_with_payments 
#             if item['payment_status']['is_fully_paid']
#         )

#         # Добавляем данные в контекст
#         context['enrollments_with_payments'] = enrollments_with_payments
#         context['total_count'] = total_count
#         context['paid_count'] = paid_count

#         return context

# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         group = self.object
        
        
        
#         # Получаем всех студентов группы
#         enrollments = group.enrollment_set.all().select_related('student')
        
#         # Подготавливаем данные о платежах для каждого студента
#         enrollments_with_payments = []
        
#         for enrollment in enrollments:
#             # Определяем следующий персональный месяц для студента
#             next_personal_month = enrollment.get_next_personal_month()
            
#             # Получаем статус оплаты за следующий месяц
#             payment_status = Payment.get_student_payment_status_by_month_number(
#                 enrollment.student, 
#                 group, 
#                 next_personal_month
#             )
            
#             enrollments_with_payments.append({
#                 'enrollment': enrollment,
#                 'payment_status': payment_status,
#                 'next_personal_month': next_personal_month,
#                 'should_check_payment': enrollment.should_check_personal_payment(),
#                 'progress_percent': enrollment.get_personal_progress_percent()
#             })
        
#         # Подсчёт количества оплативших и общего числа
#         enrollments_with_payments = context['enrollments_with_payments']
#         total_count = len(enrollments_with_payments)
#         paid_count = sum(
#             1 for item in enrollments_with_payments 
#             if item['payment_status']['is_fully_paid']
#         )
        
#         context['total_count'] = total_count
#         context['paid_count'] = paid_count
#         context['enrollments_with_payments'] = enrollments_with_payments
        
        
#         return context
# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object
        
#         # Определяем месяц, за который проверяем оплату
#         check_payment_month = self.get_payment_check_month(group)
        
#         # Получаем всех студентов группы
#         enrollments = group.enrollment_set.all().select_related('student')
        
#         # Подготавливаем данные о платежах для каждого студента
#         enrollments_with_payments = []
        
#         for enrollment in enrollments:
#             payment_status = Payment.get_student_payment_status(
#                 enrollment.student, 
#                 group, 
#                 check_payment_month
#             )
            
#             enrollments_with_payments.append({
#                 'enrollment': enrollment,
#                 'payment_status': payment_status,
#                 'check_month': check_payment_month
#             })
        
#         # Передаем данные в контекст
#         context['enrollments_with_payments'] = enrollments_with_payments
#         context['should_check_payment'] = group.should_check_payment()
#         context['next_month'] = group.get_next_month()
#         context['check_payment_month'] = check_payment_month
        
#         return context
    
    def get_payment_check_month(self, group):
        """
        Определяет, за какой месяц проверять оплату
        Если группа завершила текущий месяц - проверяем следующий
        """
        if group.should_check_payment():
            # Проверяем оплату за следующий месяц
            check_month = group.start_date + relativedelta(months=group.get_next_month() - 1)
        else:
            # Проверяем оплату за текущий месяц
            check_month = group.start_date + relativedelta(months=group.get_current_month() - 1)
        
        return check_month.replace(day=1)
    
    
    
# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object
        
#         # Получаем всех студентов группы с информацией о зачислениях
#         enrollments = group.enrollment_set.all().select_related('student')
        
#         # Добавляем информацию о платежах каждого студента
#         enrollments_with_payments = []
#         next_month = group.get_next_month()
        
#         for enrollment in enrollments:
#             # Проверяем, оплачен ли следующий месяц
#             is_paid = PaymentDate.get_student_payment_status(
#                 enrollment.student, 
#                 group, 
#                 next_month
#             )
            
#             # Сумма долга: стоимость месяца, если не оплачено
#             amount_due = group.monthly_price if not is_paid else 0
            
#             enrollments_with_payments.append({
#                 'enrollment': enrollment,
#                 'is_paid': is_paid,
#                 'amount_due': amount_due
#             })
        
#         # Передаем все необходимые переменные в контекст
#         context['enrollments_with_payments'] = enrollments_with_payments
#         context['should_check_payment'] = group.should_check_payment()
#         context['next_month'] = next_month
#         context['enrollments'] = enrollments  # Добавляем обычные enrollments для совместимости
        
#         return context
# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object
        
#         # Добавляем информацию о платежах каждого студента
#         enrollments_with_payments = []
#         for enrollment in group.enrollment_set.all():
#             total_paid = Payment.objects.filter(
#                 student=enrollment.student,
#                 group=group
#             ).aggregate(total=Sum('amount'))['total'] or 0
            
#             # Проверяем, хватает ли средств для оплаты текущего месяца
#             current_month = group.get_current_month()
#             is_paid = total_paid >= (group.monthly_price * current_month)
            
#             enrollments_with_payments.append({
#                 'enrollments': enrollment,
#                 'total_paid': total_paid,
#                 'is_paid': is_paid,
#                 'amount_due': max(0, (group.monthly_price * current_month) - total_paid)
#             })
        
#         context['enrollments_with_payments'] = enrollments_with_payments
#         return context
# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object

#         student_payment_status = {}
#         next_month = group.get_next_month()

#         for enrollment in group.enrollment_set.all():
#             is_paid = group.get_student_payment_status(
#                 enrollment.student,
#                 next_month
#             )
#             student_payment_status[enrollment.student.id] = {
#                 'is_paid': is_paid,
#                 'enrollment': enrollment
#             }
#         enrollments = Enrollment.objects.filter(group=group).select_related('student')
#         context['enrollments'] = enrollments
#         context['student_payment_status'] = student_payment_status
#         context['next_month'] = next_month
#         return context

# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group = self.object
        
#         # Получаем всех студентов группы с информацией о зачислениях
#         enrollments = Enrollment.objects.filter(group=group).select_related('student')
        
#         # Подготавливаем данные для отображения статуса оплаты
#         student_status = {}
#         for enrollment in enrollments:
#             status = group.get_student_payment_status(enrollment.student)
#             student_status[enrollment.student.id] = {
#                 'status': status,
#                 'enrollment': enrollment
#             }
        
#         context['student_status'] = student_status
#         context['enrollments'] = enrollments
#         context['should_check_payment'] = group.should_check_payment()
#         context['next_month'] = group.get_next_month()
        
#         return context

class MarkStudentAttendanceView(LoginRequiredMixin, View):
    """View для отметки посещения конкретного студента"""
    
    def post(self, request, group_id, student_id):
        group = get_object_or_404(Group, pk=group_id)
        enrollment = get_object_or_404(
            Enrollment, 
            group=group, 
            student_id=student_id
        )
        
        enrollment.increment_attendance()
        messages.success(
            request, 
            f'Посещение отмечено для {enrollment.student.full_name}. Всего: {enrollment.lessons_attended}'
        )
        
        return redirect('group_detail', pk=group_id)
# class MarkStudentAttendanceView(LoginRequiredMixin, View):
#     """View для отметки посещения конкретного студента"""
    
#     def post(self, request, group_id, student_id):
#         group = get_object_or_404(Group, pk=group_id)
#         enrollment = get_object_or_404(
#             Enrollment, 
#             group=group, 
#             student_id=student_id
#         )
        
#         enrollment.increment_attendance()
#         messages.success(
#             request, 
#             f'Посещение отмечено для {enrollment.student.full_name}. Всего: {enrollment.lessons_attended}'
#         )
        
#         return redirect('group_detail', pk=group_id)

# class GroupDetailView(LoginRequiredMixin, DetailView):
#     model = Group
#     template_name = 'groups/group_detail.html'
#     context_object_name = 'group'