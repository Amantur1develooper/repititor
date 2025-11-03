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

from .models import Group, Enrollment, AttendanceLog
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
        enrollments = Enrollment.objects.filter(group=group).select_related('student')

        for enrollment in enrollments:
            enrollment.increment_attendance(
                by_user=request.user,
                source=AttendanceLog.Source.BULK
            )

        messages.success(request, 'Занятие добавлено для всех студентов группы')
        return redirect('group_detail', pk=group.pk)
    
    
# class GroupIncrementLessonView(LoginRequiredMixin, View):
#     """View для увеличения счетчика занятий группы"""
    
#     def post(self, request, pk):
#         group = get_object_or_404(Group, pk=pk)


        
#         # Увеличиваем счетчики посещений для всех студентов группы
#         enrollments = Enrollment.objects.filter(group=group)
#         for enrollment in enrollments:
#             enrollment.increment_attendance()
        
#         messages.success(
#             request, 
#             f'Занятие добавлено для всех студентов группы'
#         )
        
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
        context['attendance_logs'] = (
    AttendanceLog.objects
    .filter(group=group)
    .select_related('enrollment__student', 'marked_by')
    .order_by('-marked_at')[:100]
)
        return context

    
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
    
    
    
    
class MarkStudentAttendanceView(LoginRequiredMixin, View):
    """View для отметки посещения конкретного студента"""
    def post(self, request, group_id, student_id):
        group = get_object_or_404(Group, pk=group_id)
        enrollment = get_object_or_404(Enrollment, group=group, student_id=student_id)

        enrollment.increment_attendance(
            by_user=request.user,
            source=AttendanceLog.Source.SINGLE
        )

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


