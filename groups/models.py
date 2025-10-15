from django.utils import timezone
from django.core.validators import MinValueValidator
from dateutil.relativedelta import relativedelta
from django.db import models
from students.models import Student
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название группы')
    students = models.ManyToManyField(Student, through='Enrollment', verbose_name='Ученики')
    start_date = models.DateField(verbose_name='Дата начала 1-го месяца обучения', default=timezone.now)
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Куратор')
    is_active = models.BooleanField(default=True, verbose_name='Активная группа')
    
    lessons_per_month = models.PositiveIntegerField(default=15, verbose_name='Занятий в месяце')
    monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Стоимость обучения в месяц',
        default=0
    )
    
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-start_date', 'name']

    def __str__(self):
        return self.name
    
    
    
    
    def students_count(self):
        return self.students.count()
    students_count.short_description = 'Количество учеников'
    

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ученик')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    enrolled_from = models.DateField(verbose_name='Дата зачисления', default=timezone.now)
    lessons_attended = models.PositiveIntegerField(default=0, verbose_name='Посещенных занятий')
    # Новое поле: с какого занятия студент начал обучение
    start_lesson = models.PositiveIntegerField(default=1, verbose_name='Начальное занятие')
    
    class Meta:
        verbose_name = 'Зачисление'
        verbose_name_plural = 'Зачисления'
        unique_together = ['student', 'group']
        
    def __str__(self):
        return f"{self.student} в {self.group}"
    
    def increment_attendance(self):
        """Увеличивает счетчик посещенных занятий"""
        self.lessons_attended += 1
        self.save()
    
    def get_personal_lesson_count(self):
        """Возвращает персональный счетчик занятий студента"""
        return self.lessons_attended
    
    def get_personal_month(self):
        """Возвращает текущий месяц обучения для студента"""
        if self.lessons_attended == 0:
            return 1
        return (self.lessons_attended - 1) // self.group.lessons_per_month + 1
    
    def get_next_personal_month(self):
        """Возвращает следующий месяц для студента"""
        return self.get_personal_month() 
    
    def should_check_personal_payment(self):
        """Проверяет, нужно ли студенту оплачивать следующий месяц"""
        return self.lessons_attended % self.group.lessons_per_month == 0 and self.lessons_attended > 0
    
    def get_personal_progress_percent(self):
        """Возвращает процент завершения текущего месяца"""
        current_lesson_in_month = self.lessons_attended % self.group.lessons_per_month
        if current_lesson_in_month == 0 and self.lessons_attended > 0:
            return 100
        return (current_lesson_in_month / self.group.lessons_per_month) * 100
