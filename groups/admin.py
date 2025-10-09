# groups/admin.py
from django.contrib import admin
from .forms import EnrollmentForm, GroupForm
from .models import Group, Enrollment
from django.utils.html import format_html

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fields = ['student', 'enrolled_from']
    autocomplete_fields = ['student']
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # form = GroupForm
    list_display = ['name', 'curator', 'monthly_price','lessons_count', 'lessons_per_month', 'get_current_month', 'is_active']
    list_filter = ['is_active', 'curator', 'start_date']
    readonly_fields = ['lessons_count', 'get_current_month']
    search_fields = ['name', 'curator__username', 'students__full_name']
    list_editable = ['is_active']
    inlines = [EnrollmentInline]
    def display_students(self, obj):
        students = obj.students.all()[:5]  # Показываем первых 5 студентов
        names = [student.full_name for student in students]
        if obj.students.count() > 5:
            names.append('...')
        return ', '.join(names) if names else 'Нет учеников'
    display_students.short_description = 'Ученики (первые 5)'



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    # form = EnrollmentForm
    list_display = ['student', 'group', 'lessons_attended', 'enrolled_from']
    list_filter = ['group', 'enrolled_from']
    search_fields = ['student__full_name', 'group__name']
    autocomplete_fields = ['student', 'group']
    date_hierarchy = 'enrolled_from'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'group')