from django.contrib import admin

from .models import Student

# class EnrollmentInline(admin.TabularInline):
#     model = Enrollment
#     extra = 1
#     fields = ['group', 'enrolled_from']
#     autocomplete_fields = ['group']
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone',  'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'phone', ]
    list_editable = ['status']
    # inlines = [EnrollmentInline] 
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name',  'status')
        }),
        ('Контактная информация', {
            'fields': ('phone','phone_parent', 'parent_guardian')
        }),
        ('Дополнительная информация', {
            'fields': ('notes',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
# students/admin.py (дополнение)




