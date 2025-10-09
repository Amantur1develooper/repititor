from django.db import models
from students.models import Student
from groups.models import Group
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Sum
from groups.models import Group
from django.core.validators import MinValueValidator
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class Payment(models.Model):
    """Модель для хранения платежей"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        verbose_name='Ученик',
        related_name='payments'
    )
    date = models.DateField(
        verbose_name='Дата платежа', 
        default=timezone.now
    )
    amount = models.DecimalField(
        verbose_name='Сумма', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    months_count = models.PositiveIntegerField(
        verbose_name='Количество месяцев', 
        default=1
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        verbose_name='Группа',
        related_name='payments'
    )
    notes = models.TextField(
        verbose_name='Примечания', 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Поле для указания месяца, за который вносится оплата
    payment_month = models.DateField(
        verbose_name='Месяц оплаты',
        help_text='Первый день месяца, за который вносится оплата'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.student} - {self.amount} - {self.date}"

    def save(self, *args, **kwargs):
        """Убеждаемся, что payment_month всегда первый день месяца"""
        if self.payment_month:
            self.payment_month = self.payment_month.replace(day=1)
        super().save(*args, **kwargs)

    @classmethod
    def get_student_payment_status(cls, student, group, target_month):
        """
        Возвращает статус оплаты студента за конкретный месяц
        target_month - первый день целевого месяца
        """
        target_month = target_month.replace(day=1)
        
        # Суммируем все платежи студента за указанный месяц в этой группе
        payments = cls.objects.filter(
            student=student,
            group=group,
            payment_month=target_month
        )
        
        total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_price = group.monthly_price
        
        return {
            'total_paid': total_paid,
            'monthly_price': monthly_price,
            'is_fully_paid': total_paid >= monthly_price,
            'is_partially_paid': 0 < total_paid < monthly_price,
            'is_not_paid': total_paid == 0,
            'remaining_amount': max(0, monthly_price - total_paid)
        }

class PaymentDate(models.Model):
    """Модель для хранения дат оплаты по месяцам"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        verbose_name='Ученик',
        related_name='payment_dates'
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        verbose_name='Группа',
        related_name='payment_dates'
    )
    payment_date = models.DateField(verbose_name='Дата оплаты')
    month_number = models.PositiveIntegerField(verbose_name='Номер месяца')
    is_paid = models.BooleanField(verbose_name='Оплачено', default=True)
    
    class Meta:
        verbose_name = 'Дата оплаты'
        verbose_name_plural = 'Даты оплат'
        unique_together = ['student', 'group', 'month_number']

    def __str__(self):
        return f"{self.student} - {self.group} - Месяц {self.month_number}"

    @classmethod
    def get_student_payment_status(cls, student, group, month_number):
        """Проверяет, оплатил ли студент конкретный месяц"""
        return cls.objects.filter(
            student=student,
            group=group,
            month_number=month_number
        ).exists()
        
    @classmethod
    def is_month_paid(cls, student, group, month_number):
        """Проверяет, оплачен ли конкретный месяц обучения"""
        return cls.objects.filter(
            student=student,
            group=group,
            month_number=month_number,
            is_paid=True
        ).exists()
    @classmethod
    def update_payment_dates(cls, student, group):
        """Обновляет даты оплаты для студента в группе с проверкой полноты оплаты"""
        payments = Payment.objects.filter(
            student=student, 
            group=group
        ).order_by('date')
        
        # Удаляем старые записи об оплаченных месяцах
        cls.objects.filter(student=student, group=group).delete()
        
        current_date = group.start_date
        month_number = 1
        accumulated_amount = 0  # Накопленная сумма платежей
        
        for payment in payments:
            accumulated_amount += payment.amount
            
            # Проверяем, хватает ли средств для оплаты месяцев
            while accumulated_amount >= group.monthly_price:
                # Создаем запись об оплаченном месяце
                cls.objects.create(
                    student=student,
                    group=group,
                    payment_date=payment.date,
                    month_number=month_number,
                    is_paid=True
                )
                
                # Вычитаем стоимость месяца из накопленной суммы
                accumulated_amount -= group.monthly_price
                month_number += 1
                current_date = cls.get_next_month_date(current_date)
    @classmethod
    def update_payment_dates(cls, student, group):
        """Обновляет даты оплаты для студента в группе"""
        # Получаем все платежи студента в этой группе
        payments = Payment.objects.filter(
            student=student, 
            group=group
        ).order_by('date')
        
        # Удаляем старые записи
        cls.objects.filter(student=student, group=group).delete()
        
        current_date = group.start_date
        month_number = 1
        
        for payment in payments:
            # Для каждого платежа создаем записи на оплаченные месяцы
            for i in range(payment.months_count):
                cls.objects.create(
                    student=student,
                    group=group,
                    payment_date=payment.date,
                    month_number=month_number
                )
                month_number += 1
                # Вычисляем дату начала следующего месяца
                current_date = cls.get_next_month_date(current_date)

    @staticmethod
    def get_next_month_date(current_date):
        """Вычисляет дату начала следующего месяца"""
        if current_date.month == 12:
            return current_date.replace(year=current_date.year + 1, month=1)
        else:
            return current_date.replace(month=current_date.month + 1)