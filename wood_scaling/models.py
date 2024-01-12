from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class WoodScaling(models.Model):
    id = models.AutoField(primary_key=True)
    weighting_day = models.DateField()
    slip_no = models.IntegerField()
    woods_type_num = models.IntegerField()
    trucks_num = models.CharField(max_length=255)
    vendor_num = models.IntegerField()
    sources_num = models.IntegerField()
    others = models.IntegerField()
    total_weight_time = models.CharField(max_length=255)
    total_weight = models.FloatField()
    empty_weight_time = models.CharField(max_length=255)
    empty_weight = models.FloatField()
    net_weight = models.FloatField()
    remarks = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

    class Meta:
        db_table = 'truck_scaling'

class WoodType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

    class Meta:
        db_table = 'wood_type'

class Forests(models.Model):
    id = models.IntegerField(primary_key=True)
    supplier_id = models.IntegerField()
    location = models.CharField(max_length=100)
    k_location = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    registration = models.CharField(max_length=100)
    authority = models.CharField(max_length=100)
    classification = models.CharField(max_length=100)
    removal = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    distance = models.CharField(max_length=100)
    document = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

    class Meta:
        db_table = 'forests'

class Supplier(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    k_name = models.CharField(max_length=100)
    registration = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    document = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

    class Meta:
        db_table = 'supplier'

