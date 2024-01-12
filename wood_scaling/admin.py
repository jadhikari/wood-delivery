from django.contrib import admin
from .models import WoodScaling, WoodType, Forests, Supplier

admin.site.register(WoodScaling)
admin.site.register(WoodType)
admin.site.register(Forests)
admin.site.register(Supplier)
