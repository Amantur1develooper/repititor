from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.decorators import role_required
from django.utils.decorators import method_decorator
from .models import Student
from .forms import StudentForm
from django.urls import reverse_lazy
# @method_decorator(role_required(['admin']), name='dispatch')
class StudentListView( ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        queryset = Student.objects.all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(full_name__icontains=search)
        
        return queryset

# @method_decorator(role_required(['admin']), name='dispatch')
class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

# @method_decorator(role_required(['admin']), name='dispatch')
class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')