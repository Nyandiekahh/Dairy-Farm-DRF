from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'assigned_farm')
    list_filter = ('is_admin', 'assigned_farm')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Farm Info', {'fields': ('is_admin', 'assigned_farm', 'phone')}),
    )

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at')
    search_fields = ('name', 'location')

@admin.register(Cow)
class CowAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'stage', 'mother', 'birth_date')
    list_filter = ('farm', 'stage')
    search_fields = ('name',)

@admin.register(ChickenBatch)
class ChickenBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_name', 'batch_number', 'farm', 'current_count', 'purchase_date')
    list_filter = ('farm',)

@admin.register(MilkProduction)
class MilkProductionAdmin(admin.ModelAdmin):
    list_display = ('cow', 'date', 'session', 'quantity', 'recorded_by')
    list_filter = ('date', 'session', 'cow__farm')

@admin.register(MilkSale)
class MilkSaleAdmin(admin.ModelAdmin):
    list_display = ('farm', 'date', 'quantity_sold', 'price_per_liter', 'total_amount')
    list_filter = ('farm', 'date')

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('farm', 'feed_type', 'quantity_remaining', 'is_finished', 'needs_restock')
    list_filter = ('farm', 'feed_type', 'is_finished', 'needs_restock')

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('cow', 'disease_name', 'date_sick', 'date_treated', 'vet_name')
    list_filter = ('date_sick', 'cow__farm')

@admin.register(EggProduction)
class EggProductionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'eggs_collected', 'recorded_by')
    list_filter = ('date', 'batch__farm')

@admin.register(RestockAlert)
class RestockAlertAdmin(admin.ModelAdmin):
    list_display = ('farm', 'alert_type', 'item_name', 'is_resolved', 'created_at')
    list_filter = ('farm', 'alert_type', 'is_resolved')