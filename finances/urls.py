from django.urls import path
from .views import FinanceReportView2, ExportFinanceReportExcelView

urlpatterns = [
    path('', FinanceReportView2.as_view(), name='finance_report'),
    path('export/excel/', ExportFinanceReportExcelView.as_view(), name='export_finance_excel'),



]