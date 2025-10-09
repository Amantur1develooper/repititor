from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.decorators import role_required
from django.utils.decorators import method_decorator
from django.db.models import Sum
from payments.models import Payment
from students.models import Student
import datetime

@method_decorator(role_required(['admin', 'accountant']), name='dispatch')
class FinanceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'finances/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Параметры фильтрации
        period = self.request.GET.get('period', 'month')
        student_id = self.request.GET.get('student')
        group_id = self.request.GET.get('group')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Базовый queryset
        payments = Payment.objects.all()

        # Применяем фильтры
        if student_id:
            payments = payments.filter(student_id=student_id)
        if group_id:
            payments = payments.filter(group_id=group_id)
        if start_date and end_date:
            payments = payments.filter(date__range=[start_date, end_date])
        else:
            # Фильтр по периоду
            today = datetime.date.today()
            if period == 'day':
                payments = payments.filter(date=today)
            elif period == 'week':
                start_week = today - datetime.timedelta(days=today.weekday())
                end_week = start_week + datetime.timedelta(days=6)
                payments = payments.filter(date__range=[start_week, end_week])
            else:  # month
                payments = payments.filter(date__year=today.year, date__month=today.month)

        # Расчеты
        total_income = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        debt_students = Student.objects.filter(status='debt')

        context.update({
            'payments': payments,
            'total_income': total_income,
            'debt_students': debt_students,
            'period': period,
        })
        return context