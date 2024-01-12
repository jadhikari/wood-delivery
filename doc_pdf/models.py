import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from wood_scaling.models import Supplier as WoodSupplier


def validate_pdf(value):
    ext = value.name.split('.')[-1].lower()
    if ext != 'pdf':
        raise ValidationError('Unsupported file extension. Only PNG files are allowed.')


class Certificate(models.Model):
    id = models.AutoField(primary_key=True)
    supplier_name = models.ForeignKey(WoodSupplier, on_delete=models.CASCADE)
    unverified_certificate = models.FileField(upload_to='certificates/unverified/', blank=True, null=True, validators=[validate_pdf])
    verified_certificate = models.FileField(upload_to='certificates/verified/', blank=True, null=True, validators=[validate_pdf])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

    def __str__(self):
        return f"Certificate {self.id} for {self.supplier_name}"
    
    class Meta:
        db_table = 'Certificate'
    


def validate_png(value):
    ext = value.name.split('.')[-1].lower()
    if ext != 'png':
        raise ValidationError('Unsupported file extension. Only PNG files are allowed.')


class SupplierLogo(models.Model):
    id = models.AutoField(primary_key=True)
    supplier_name = models.ForeignKey(WoodSupplier, on_delete=models.CASCADE, unique=True)
    email = models.EmailField(unique=True, blank=False)
    stamp = models.ImageField(upload_to='images/supplier_logos/', blank=False, null=False, validators=[validate_png])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

    # def logo_thumbnail_url(self):
    #     if self.stamp:
    #         return f"{settings.MEDIA_URL}{self.stamp.name}"
    #     return None

    def __str__(self):
        return f"SupplierLogo {self.id} for {self.supplier_name}"
    
    class Meta:
        db_table = 'SupplierLogo'

    
    
    


