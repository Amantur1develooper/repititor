# payments/admin.py
from django.contrib import admin
from .models import Payment, PaymentDate


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'group',
        'amount',
        'payment_month_number',
        'date',
        'notes_short',
        'created_at',
    )
    list_filter = (
        'group',
        'date',
        'payment_month_number',
    )
    # ВАЖНО: тут подставь реальные поля модели Student
    # Если у студента есть поле full_name – так и оставляем
    search_fields = (
        'student__full_name',   # если поле называется иначе – поменяй
        'group__name',
        'notes',
    )
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    autocomplete_fields = ('student', 'group')
    readonly_fields = ('created_at',)
    list_select_related = ('student', 'group')

    fieldsets = (
        ('Основная информация', {
            'fields': ('student', 'group', 'date', 'amount')
        }),
        ('Период оплаты', {
            'fields': ('payment_month_number',)
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at')
        }),
    )

    def notes_short(self, obj):
        if not obj.notes:
            return ''
        return (obj.notes[:30] + '…') if len(obj.notes) > 30 else obj.notes
    notes_short.short_description = 'Примечания'


@admin.register(PaymentDate)
class PaymentDateAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'group',
        'month_number',
        'payment_date',
        'paid_amount',
        'required_amount',
        'is_paid',
        'status_display',
    )
    list_filter = (
        'group',
        'is_paid',
        'month_number',
    )
    # Тут тоже используем имя поля студента, по которому хочешь искать
    search_fields = (
        'student__full_name',   # замени, если поле у Student другое
        'group__name',
    )
    date_hierarchy = 'payment_date'
    ordering = ('student', 'group', 'month_number')
    autocomplete_fields = ('student', 'group')
    list_select_related = ('student', 'group')

    # Эти поля лучше не править руками — они считаются из платежей
    readonly_fields = (
        'student',
        'group',
        'payment_date',
        'month_number',
        'is_paid',
        'paid_amount',
        'required_amount',
    )

    fieldsets = (
        ('Ученик и группа', {
            'fields': ('student', 'group')
        }),
        ('Месяц и дата оплаты', {
            'fields': ('month_number', 'payment_date', 'is_paid')
        }),
        ('Суммы', {
            'fields': ('paid_amount', 'required_amount')
        }),
    )

    def has_add_permission(self, request):
        """Новые записи создаются автоматически из Payment.update_payment_dates"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Удаление тоже лучше не разрешать — всё обновляется из платежей"""
        return False

    def status_display(self, obj):
        if obj.paid_amount >= obj.required_amount and obj.required_amount > 0:
            return 'Полностью оплачено'
        if obj.paid_amount > 0:
            return 'Частично оплачено'
        return 'Не оплачено'
    status_display.short_description = 'Статус'
