# groups/urls.py
from django.urls import path
from .views import GroupIncrementLessonView, GroupListView, GroupCreateView, GroupUpdateView, GroupDetailView, MarkStudentAttendanceView

urlpatterns = [
    path('', GroupListView.as_view(), name='group_list'),
    path('create/', GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/update/', GroupUpdateView.as_view(), name='group_update'),
    path('<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
    path('<int:pk>/increment_lesson/', GroupIncrementLessonView.as_view(), name='group_increment_lesson'),
    path('<int:group_id>/student/<int:student_id>/attendance/', MarkStudentAttendanceView.as_view(), name='mark_student_attendance'),
]