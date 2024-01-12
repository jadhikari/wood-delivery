from django import forms
from django.contrib import admin
from .models import WoodScaling, Supplier, Forests
from datetime import date

class DownloadForm(forms.Form):
    selected_data = forms.ModelMultipleChoiceField(queryset=WoodScaling.objects.all(), widget=forms.CheckboxSelectMultiple)

class RemarksForm(forms.Form):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))


class AddSupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['by_user']
        fields = '__all__'

    def clean_id(self):
        id = str(self.cleaned_data['id'])  # Convert to string
        if len(id) != 3 or not id.isdigit():
            raise forms.ValidationError('ID must be a 3-digit number.')
        return id

class SupplierEditForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['by_user']  # Include all fields except the ID field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable the ID field
        self.fields['id'].disabled = True


class ForestsEditForm(forms.ModelForm):
    class Meta:
        model = Forests
        exclude = ['by_user']  # Include all fields except the ID field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable the ID field
        self.fields['id'].disabled = True
        self.fields['supplier_id'].disabled = True
        #field type for date
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        #field type 
        self.fields['classification'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['removal'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        #firld type for number
        self.fields['area'].widget = forms.NumberInput(attrs={'type': 'text'})
        self.fields['distance'].widget = forms.NumberInput(attrs={'type': 'text'})


class AddForestForm(forms.ModelForm):
    class Meta:
        model = Forests
        fields = ['supplier_id','id','location', 'k_location', 'registration', 'date', 'authority', 'classification', 'removal',
                  'area', 'distance', 'document']

    def clean_id(self):
        id = str(self.cleaned_data['id'])  # Convert to string
        if len(id) != 3 or not id.isdigit():
            raise forms.ValidationError('ID must be a 3-digit number.')
        return id 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable the ID field
        self.fields['supplier_id'].disabled = True
        #field type for date
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        #field type 
        self.fields['classification'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['removal'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        #firld type for number
        self.fields['area'].widget = forms.NumberInput(attrs={'type': 'text'})
        self.fields['distance'].widget = forms.NumberInput(attrs={'type': 'text'})     

# class WoodScalingSearchForm(forms.Form):
#     start_date = forms.DateField( required=False, widget=forms.DateInput(attrs={'type': 'date'}))
#     end_date = forms.DateField( required=False, widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY/MM/DD'}))
#     vendor_name = forms.ChoiceField(choices=[('', 'Select Vendor')] + [(supplier.id, supplier.name) for supplier in Supplier.objects.all()], required=False)
#     wood_source = forms.ChoiceField(choices=[('', 'Select Wood Source')] + [(forest.id, forest.location) for forest in Forests.objects.all()], required=False)
        

class WoodScalingSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY/MM/DD'}))
    vendor_name = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name='name',
        label='Vendor Name',
        required=False
    )
    wood_source = forms.ModelChoiceField(
        queryset=Forests.objects.all(),
        to_field_name='location',
        label='Wood Source',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor_name'].choices = [('', 'Select Vendor')] + [(supplier.id, supplier.name) for supplier in Supplier.objects.all()]
        self.fields['wood_source'].choices = [('', 'Select Wood Source')] + [(forest.id, forest.location) for forest in Forests.objects.all()]


class UploadFileForm(forms.Form):
    file = forms.FileField()
 