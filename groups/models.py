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
        verbose_name = 'Группа студента'
        verbose_name_plural = 'Группы студентов'
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
    
    
    def increment_attendance(self, by_user=None, source='single', note: str = ''):
        """
        Увеличивает счётчик посещений и пишет запись в AttendanceLog — атомарно.
        :param by_user: User, кто отметил
        :param source: 'single' | 'bulk'
        :param note: необязательная пометка
        """
        from .models import AttendanceLog  # локальный импорт, чтобы избежать циклов

        with transaction.atomic():
            # +1 к посещениям (через F-выражение без гонок)
            type(self).objects.filter(pk=self.pk).update(lessons_attended=F('lessons_attended') + 1)
            # перечитать фактическое значение
            self.refresh_from_db(fields=['lessons_attended'])

            AttendanceLog.objects.create(
            enrollment=self,
            group=self.group,
            marked_by=by_user,
            source=source,
            lesson_no_at_time=self.lessons_attended,
            note=note
        )

    # def increment_attendance(self):
    #     """Увеличивает счетчик посещенных занятий"""
    #     self.lessons_attended += 1
    #     self.save()
    
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
# groups/models.py
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.conf import settings

# ... твои Group, Enrollment и т.д. выше

class AttendanceLog(models.Model):
    class Source(models.TextChoices):
        SINGLE = "single", "Индивидуально (кнопка у студента)"
        BULK = "bulk", "Групповое (кнопка «занятие для всех»)"

    enrollment = models.ForeignKey(
        'groups.Enrollment',
        on_delete=models.CASCADE,
        related_name='attendance_logs',
        verbose_name='Запись зачисления'
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='attendance_logs',
        verbose_name='Группа',
        db_index=True
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='attendance_marked',
        verbose_name='Кто отметил'
    )
    marked_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Когда отмечено',
        db_index=True
    )
    source = models.CharField(
        max_length=12,
        choices=Source.choices,
        default=Source.SINGLE,
        verbose_name='Источник отметки'
    )
    lesson_no_at_time = models.PositiveIntegerField(
        default=0,
        verbose_name='Номер занятия у студента на момент отметки'
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Примечание'
    )

    class Meta:
        verbose_name = 'Лог посещаемости'
        verbose_name_plural = 'Логи посещаемости'
        ordering = ['-marked_at']
        indexes = [
            models.Index(fields=['group', '-marked_at']),
            models.Index(fields=['enrollment', '-marked_at']),
        ]

    def __str__(self):
        sname = getattr(self.enrollment.student, 'full_name', str(self.enrollment.student_id))
        return f"{sname} @ {self.marked_at:%Y-%m-%d %H:%M} ({self.get_source_display()})"



# внутри класса Enrollment (groups/models.py)
from django.db import transaction
