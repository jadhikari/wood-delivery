from django.urls import path
from .views import verification, supplier_logo,edit_supplier_logo, verify_and_edit_pdf

urlpatterns = [
    # other URL patterns
    path('verification/', verification, name='verification'),
    path('supplier_logo/', supplier_logo, name='supplier_logo'),
    path('supplier_logo/edit/<int:logo_id>/', edit_supplier_logo, name='edit_supplier_logo'),
    path('verify-and-edit-pdf/<int:certificate_id>/', verify_and_edit_pdf, name='verify_and_edit_pdf'),
    
]
