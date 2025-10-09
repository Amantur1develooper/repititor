from django.urls import path
from .views import (
    PaymentListView, PaymentUpdateView,
    StudentPaymentHistoryView, GroupPaymentStatusView, payment_create
)

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment_list'),
    path('create/', payment_create, name='payment_create'),
    path('<int:pk>/update/', PaymentUpdateView.as_view(), name='payment_update'),
    path('student/<int:student_id>/history/', StudentPaymentHistoryView.as_view(), name='student_payment_history'),
    path('group/<int:pk>/status/', GroupPaymentStatusView.as_view(), name='group_payment_status'),
]
