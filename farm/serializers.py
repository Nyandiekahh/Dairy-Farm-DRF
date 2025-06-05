from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_admin', 'assigned_farm', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'

class CowSerializer(serializers.ModelSerializer):
    mother_name = serializers.CharField(source='mother.name', read_only=True)
    calves = serializers.SerializerMethodField()
    
    class Meta:
        model = Cow
        fields = '__all__'
    
    def get_calves(self, obj):
        calves = Cow.objects.filter(mother=obj)
        return [{'id': calf.id, 'name': calf.name} for calf in calves]

class ChickenBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChickenBatch
        fields = '__all__'

class MilkProductionSerializer(serializers.ModelSerializer):
    cow_name = serializers.CharField(source='cow.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    
    class Meta:
        model = MilkProduction
        fields = '__all__'
        read_only_fields = ('recorded_by',)

class MilkSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkSale
        fields = '__all__'
        read_only_fields = ('recorded_by',)

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'

class FeedConsumptionSerializer(serializers.ModelSerializer):
    cow_name = serializers.CharField(source='cow.name', read_only=True)
    feed_type = serializers.CharField(source='feed.feed_type', read_only=True)
    
    class Meta:
        model = FeedConsumption
        fields = '__all__'
        read_only_fields = ('recorded_by',)

class HealthRecordSerializer(serializers.ModelSerializer):
    cow_name = serializers.CharField(source='cow.name', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ('recorded_by',)

class EggProductionSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.batch_name', read_only=True)
    
    class Meta:
        model = EggProduction
        fields = '__all__'
        read_only_fields = ('recorded_by',)

class ChickenFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChickenFeed
        fields = '__all__'

class RestockAlertSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = RestockAlert
        fields = '__all__'
        read_only_fields = ('created_by',)