from django.urls import path
from professionalServices import views

urlpatterns = [
    #region professional services
    path('professional_services_invoice/<int:library_id>&<int:invoice_id>', views.professional_services_invoice, name='professional_services_invoice'),
    path('professional_services_invoice_paid_submission/<int:library_id>&<int:invoice_id>', views.professional_services_invoice_paid_submission, name='professional_services_invoice_paid_submission'),
    path('portfolio/', views.portfolio, name='portfolio'),

    #endregion
]