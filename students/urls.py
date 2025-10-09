from django.urls import path
from . import views
from .views import StudentListView, StudentCreateView, StudentUpdateView

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('create/', StudentCreateView.as_view(), name='student_create'),
    path('<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
]