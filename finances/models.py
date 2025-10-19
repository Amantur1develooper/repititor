from django.db import models
from students.models import Student
from groups.models import Group
from payments.models import Payment
from django.utils import timezone
from django.core.validators import MinValueValidator

class FinancialReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('daily', 'Ежедневный'),
        ('weekly', 'Еженедельный'),
        ('monthly', 'Ежемесячный'),
        ('custom', 'Произвольный период'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название отчета')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES, verbose_name='Тип отчета')
    start_date = models.DateField(verbose_name='Начальная дата')
    end_date = models.DateField(verbose_name='Конечная дата')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='Создатель')
    
    # Поля для хранения результатов (кеширование)
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общий доход')
    total_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общая задолженность')
    
    class Meta:
        verbose_name = 'Финансовый отчет'
        verbose_name_plural = 'Финансовые отчеты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    def calculate_totals(self):
        """Пересчитывает итоговые суммы отчета"""
        from django.db.models import Sum, Q
        from payments.models import Payment
        
        # Доходы за период
        payments = Payment.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        self.total_income = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Задолженности (студенты с долгами)
        # Здесь нужно доработать логику расчета долгов
        self.total_debt = 0  # Временное значение
        
        self.save()