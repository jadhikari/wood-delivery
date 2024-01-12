import os
from django import forms
from wood_scaling.models import Supplier as WoodSupplier
from .models import Certificate , SupplierLogo


class CertificateForm(forms.ModelForm):
    supplier_name = forms.ModelChoiceField(
        queryset=WoodSupplier.objects.all(),
        to_field_name='name',
        label='Supplier Name'
    )

    class Meta:
        model = Certificate
        fields = ['id','supplier_name', 'unverified_certificate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier_name'].choices = [('', 'Select')] + [(supplier.name, supplier.name) for supplier in WoodSupplier.objects.all()]
        self.fields['supplier_name'].required = True
        self.fields['unverified_certificate'].required = True



class SupplierLogoForm(forms.ModelForm):
    supplier_name = forms.ModelChoiceField(
        queryset=WoodSupplier.objects.all(),
        to_field_name='name',
        label='Supplier Name'
    )

    class Meta:
        model = SupplierLogo
        fields = ['supplier_name', 'email', 'stamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier_name'].choices = [('', 'Select')] + [(supplier.name, supplier.name) for supplier in WoodSupplier.objects.all()]
        

class EditSupplierLogoForm(forms.ModelForm):
    class Meta:
        model = SupplierLogo
        fields = ['email', 'stamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'email' field non-editable
        self.fields['email'].widget.attrs['edit'] = True
        