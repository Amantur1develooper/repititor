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

from django.db import models
from students.models import Student
from groups.models import Group
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Sum
from dateutil.relativedelta import relativedelta

class Payment(models.Model):
    
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
    
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        verbose_name='Группа',
        related_name='payments'
    )
    payment_month_number = models.PositiveIntegerField(
        verbose_name='Номер месяца оплаты',
        help_text='Номер месяца (1, 2, 3...), за который вносится оплата'
    )
    # payment_month = models.DateField(
    #     verbose_name='Месяц оплаты',
    #     help_text='Первый день месяца, за который вносится оплата'
    # )
    notes = models.TextField(
        verbose_name='Примечания', 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.student} - {self.amount} - {self.date}"
    
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)
        # ОБНОВЛЯЕМ СТАТУСЫ ПОСЛЕ СОХРАНЕНИЯ ПЛАТЕЖА
        PaymentDate.update_payment_dates(self.student, self.group)
        
    @classmethod
    def get_student_payment_status(cls, student, group, month_number):
        """Получает статус оплаты по номеру месяца - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        print(f"DEBUG: Поиск платежей для {student.full_name}, месяц {month_number}")
        
        # Ищем платежи по номеру месяца, а не по дате
        payments = cls.objects.filter(
            student=student,
            group=group,
            payment_month_number=month_number  # Используем номер месяца!
        )
        
        # Отладочная информация
        found_payments = list(payments)
        print(f"DEBUG: Найдено платежей: {len(found_payments)}")
        for p in found_payments:
            print(f"DEBUG: Платеж: {p.amount}, месяц: {p.payment_month_number}")
        
        total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_price = group.monthly_price
        
        print(f"DEBUG: Итого оплачено: {total_paid}, требуется: {monthly_price}")
        
        return {
            'total_paid': total_paid,
            'monthly_price': monthly_price,
            'is_fully_paid': total_paid >= monthly_price,
            'is_partially_paid': 0 < total_paid < monthly_price,
            'is_not_paid': total_paid == 0,
            'remaining_amount': max(0, monthly_price - total_paid)
        } 
    # @classmethod
    # def get_student_payment_status(cls, student, group, month_number):
    #     """Получает статус оплаты по номеру месяца"""
    #     payments = cls.objects.filter(
    #         student=student,
    #         group=group,
    #         payment_month_number=month_number
    #     )
        
    #     total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    #     monthly_price = group.monthly_price
        
    #     return {
    #         'total_paid': total_paid,
    #         'monthly_price': monthly_price,
    #         'is_fully_paid': total_paid >= monthly_price,
    #         'is_partially_paid': 0 < total_paid < monthly_price,
    #         'is_not_paid': total_paid == 0,
    #         'remaining_amount': max(0, monthly_price - total_paid)
    #     }
    # @classmethod
    # def get_student_payment_status(cls, student, group, target_month):
        
    #     target_month = target_month.replace(day=1)
        
        
    #     payments = cls.objects.filter(
    #         student=student,
    #         group=group,
    #         payment_month=target_month
    #     )
        
    #     total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    #     monthly_price = group.monthly_price
        
    #     return {
    #         'total_paid': total_paid,
    #         'monthly_price': monthly_price,
    #         'is_fully_paid': total_paid >= monthly_price,
    #         'is_partially_paid': 0 < total_paid < monthly_price,
    #         'is_not_paid': total_paid == 0,
    #         'remaining_amount': max(0, monthly_price - total_paid)
    #     }

    @classmethod
    def get_student_payment_status_by_month_number(cls, student, group, month_number):
        """Получает статус оплаты по номеру месяца (1, 2, 3...)"""
        # Вычисляем дату месяца на основе start_date группы и номера месяца
        month_date = group.start_date + relativedelta(months=month_number-1)
        return cls.get_student_payment_status(student, group, month_date)
# class Payment(models.Model):
#     """Модель для хранения платежей"""
#     student = models.ForeignKey(
#         Student, 
#         on_delete=models.CASCADE, 
#         verbose_name='Ученик',
#         related_name='payments'
#     )
#     date = models.DateField(
#         verbose_name='Дата платежа', 
#         default=timezone.now
#     )
#     amount = models.DecimalField(
#         verbose_name='Сумма', 
#         max_digits=10, 
#         decimal_places=2,
#         validators=[MinValueValidator(0)]
#     )
#     months_count = models.PositiveIntegerField(
#         verbose_name='Количество месяцев', 
#         default=1
#     )
#     group = models.ForeignKey(
#         Group, 
#         on_delete=models.CASCADE, 
#         verbose_name='Группа',
#         related_name='payments'
#     )
#     notes = models.TextField(
#         verbose_name='Примечания', 
#         blank=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     # Поле для указания месяца, за который вносится оплата
#     payment_month = models.DateField(
#         verbose_name='Месяц оплаты',
#         help_text='Первый день месяца, за который вносится оплата'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         verbose_name = 'Платеж'
#         verbose_name_plural = 'Платежи'
#         ordering = ['-date', '-created_at']

#     def __str__(self):
#         return f"{self.student} - {self.amount} - {self.date}"

#     def save(self, *args, **kwargs):
#         """Убеждаемся, что payment_month всегда первый день месяца"""
#         if self.payment_month:
#             self.payment_month = self.payment_month.replace(day=1)
#         super().save(*args, **kwargs)

#     @classmethod
#     def get_student_payment_status(cls, student, group, target_month):
#         """
#         Возвращает статус оплаты студента за конкретный месяц
#         target_month - первый день целевого месяца
#         """
#         target_month = target_month.replace(day=1)
        
#         # Суммируем все платежи студента за указанный месяц в этой группе
#         payments = cls.objects.filter(
#             student=student,
#             group=group,
#             payment_month=target_month
#         )
        
#         total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
#         monthly_price = group.monthly_price
        
#         return {
#             'total_paid': total_paid,
#             'monthly_price': monthly_price,
#             'is_fully_paid': total_paid >= monthly_price,
#             'is_partially_paid': 0 < total_paid < monthly_price,
#             'is_not_paid': total_paid == 0,
#             'remaining_amount': max(0, monthly_price - total_paid)
#         }
class PaymentDate(models.Model):
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
    # ДОБАВЛЯЕМ: информация о частичной оплате
    paid_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Оплаченная сумма'
    )
    required_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Требуемая сумма'
    )
    
    class Meta:
        verbose_name = 'Дата оплаты'
        verbose_name_plural = 'Даты оплат'
        unique_together = ['student', 'group', 'month_number']

    def __str__(self):
        status = "Частично" if self.paid_amount < self.required_amount else "Полностью"
        return f"{self.student} - {self.group} - Месяц {self.month_number} ({status})"

    
    
    @classmethod
    
    
    def update_payment_dates(cls, student, group):
        """Обновляет даты оплаты с учетом частичных платежей"""
        payments = Payment.objects.filter(
            student=student, 
            group=group
        ).order_by('date')
        
        # Удаляем старые записи
        cls.objects.filter(student=student, group=group).delete()
        
        # Группируем платежи по месяцам
        payments_by_month = {}
        for payment in payments:
            month = payment.payment_month_number
            if month not in payments_by_month:
                payments_by_month[month] = 0
            payments_by_month[month] += payment.amount
        
        # Создаем записи для каждого месяца
        for month_number, total_paid in payments_by_month.items():
            monthly_price = group.monthly_price
            is_fully_paid = total_paid >= monthly_price
            
            # Находим дату первого платежа за этот месяц
            first_payment = payments.filter(
                payment_month_number=month_number
            ).first()
            
            cls.objects.create(
                student=student,
                group=group,
                payment_date=first_payment.date if first_payment else timezone.now(),
                month_number=month_number,
                is_paid=is_fully_paid,
                paid_amount=total_paid,
                required_amount=monthly_price
            )
# class PaymentDate(models.Model):
#     """Модель для хранения дат оплаты по месяцам"""
#     student = models.ForeignKey(
#         Student, 
#         on_delete=models.CASCADE, 
#         verbose_name='Ученик',
#         related_name='payment_dates'
#     )
#     group = models.ForeignKey(
#         Group, 
#         on_delete=models.CASCADE, 
#         verbose_name='Группа',
#         related_name='payment_dates'
#     )
#     payment_date = models.DateField(verbose_name='Дата оплаты')
#     month_number = models.PositiveIntegerField(verbose_name='Номер месяца')
#     is_paid = models.BooleanField(verbose_name='Оплачено', default=True)
    
#     class Meta:
#         verbose_name = 'Дата оплаты'
#         verbose_name_plural = 'Даты оплат'
#         unique_together = ['student', 'group', 'month_number']

#     def __str__(self):
#         return f"{self.student} - {self.group} - Месяц {self.month_number}"

#     @classmethod
#     def get_student_payment_status(cls, student, group, month_number):
#         """Проверяет, оплатил ли студент конкретный месяц"""
#         return cls.objects.filter(
#             student=student,
#             group=group,
#             month_number=month_number
#         ).exists()
        
#     @classmethod
#     def is_month_paid(cls, student, group, month_number):
#         """Проверяет, оплачен ли конкретный месяц обучения"""
#         return cls.objects.filter(
#             student=student,
#             group=group,
#             month_number=month_number,
#             is_paid=True
#         ).exists()
#     @classmethod
#     def update_payment_dates(cls, student, group):
#         """Обновляет даты оплаты для студента в группе - ТОЛЬКО ОДИН МЕТОД"""
#         payments = Payment.objects.filter(
#             student=student, 
#             group=group
#         ).order_by('date')
        
#         # Удаляем старые записи
#         cls.objects.filter(student=student, group=group).delete()
        
#         current_date = group.start_date
#         month_number = 1
#         accumulated_amount = 0  # Накопленная сумма платежей
        
#         for payment in payments:
#             accumulated_amount += payment.amount
            
#             # Проверяем, хватает ли средств для оплаты месяцев
#             while accumulated_amount >= group.monthly_price:
#                 # Создаем запись об оплаченном месяце
#                 cls.objects.create(
#                     student=student,
#                     group=group,
#                     payment_date=payment.date,
#                     month_number=month_number,
#                     is_paid=True
#                 )
                
#                 # Вычитаем стоимость месяца из накопленной суммы
#                 accumulated_amount -= group.monthly_price
#                 month_number += 1
#                 current_date = cls.get_next_month_date(current_date)



#     @staticmethod
#     def get_next_month_date(current_date):
#         """Вычисляет дату начала следующего месяца"""
#         if current_date.month == 12:
#             return current_date.replace(year=current_date.year + 1, month=1)
#         else:
#             return current_date.replace(month=current_date.month + 1)
  
    
    