from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('completed', 'Завершил обучение'),
        ('debt', 'В долге'),
    ]

    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='E-mail', blank=True)
    parent_guardian = models.CharField(max_length=255, verbose_name='Родитель/опекун', blank=True)
    notes = models.TextField(verbose_name='Примечания', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'

    def __str__(self):
        return self.full_name