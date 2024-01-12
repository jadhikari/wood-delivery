from django.urls import path
from .views import wood_scaling_list, download_certificate, details_page, supplier, edit_supplier, add_supplier, show_forests_data, edit_forests, add_forest, upload_csv, welcome
urlpatterns = [
    path('', welcome, name='welcome'),
    path('list/', wood_scaling_list, name='wood_scaling_list'),
    path('download_certificate/', download_certificate, name='download_certificate'),
    path('wood_scaling/<int:entry_id>/details/', details_page, name='details_page'),
    path('supplier/', supplier, name='supplier_list'),
    path('supplier/<int:supplier_id>/edit/', edit_supplier, name='edit_supplier'),
    path('supplier/add/', add_supplier, name='add_supplier'),
    path('supplier/<int:supplier_id>/list/', show_forests_data, name='show_forests_data'),
    path('supplier/<int:supplier_id>/forests_list/<int:forest_id>/edit/', edit_forests, name='edit_forests'),
    path('supplier/<int:supplier_id>/add_forest/', add_forest, name='add_forest'),
    path('upload_csv/', upload_csv, name='upload_csv'),
]