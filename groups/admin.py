# groups/admin.py
from django.contrib import admin
from .models import Group, Enrollment

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    autocomplete_fields = ['student']
    fields = ('student', 'enrolled_from', 'lessons_attended', 'start_lesson')
    readonly_fields = ()
    show_change_link = True

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'curator',
        'start_date',
        'students_count',
        'lessons_per_month',
        'monthly_price',
        'is_active',
    )
    list_filter = ('is_active', 'curator', 'start_date')
    search_fields = ('name', 'curator__username')
    date_hierarchy = 'start_date'
    ordering = ('-start_date', 'name')
    list_editable = ('is_active', 'monthly_price', 'lessons_per_month')
    readonly_fields = ('students_count',)
    inlines = [EnrollmentInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'curator', 'start_date', 'is_active')
        }),
        ('Обучение и оплата', {
            'fields': ('lessons_per_month', 'monthly_price')
        }),
        ('Ученики', {
            'fields': ('students_count',)
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'group',
        'enrolled_from',
        'lessons_attended',
        'start_lesson',
        'get_personal_month',
        'get_personal_progress_percent_display',
    )
    list_filter = ('group', 'enrolled_from')
    search_fields = ('student__first_name', 'student__last_name', 'group__name')
    ordering = ('-enrolled_from',)
    list_editable = ('lessons_attended', 'start_lesson')

    def get_personal_progress_percent_display(self, obj):
        """Отображает процент прогресса красиво"""
        return f"{obj.get_personal_progress_percent():.0f}%"
    get_personal_progress_percent_display.short_description = 'Прогресс'

    readonly_fields = ('get_personal_progress_percent_display',)

    fieldsets = (
        ('Общая информация', {
            'fields': ('student', 'group', 'enrolled_from', 'start_lesson')
        }),
        ('Посещаемость', {
            'fields': ('lessons_attended', 'get_personal_progress_percent_display')
        }),
    )
