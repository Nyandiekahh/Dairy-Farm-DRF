#!/usr/bin/env python3
"""
Simple debug script - uses Django management command
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dairy_farm.settings')
django.setup()

from rest_framework.test import APIClient
from datetime import date
from farm.models import *
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_specific_endpoints():
    print("🔍 DEBUGGING SPECIFIC API ENDPOINTS...")
    print("=" * 50)
    
    client = APIClient()
    
    # Get or create test users
    try:
        admin_user = User.objects.get(username='admin@test.com')
        print("✅ Found existing admin user")
    except User.DoesNotExist:
        print("❌ No admin user found - please run: python3 manage.py createsuperuser")
        return
    
    try:
        nakuru_farm = Farm.objects.filter(name__icontains='Nakuru').first()
        if nakuru_farm:
            print(f"✅ Found farm: {nakuru_farm.name}")
        else:
            print("❌ No Nakuru farm found - creating one...")
            nakuru_farm = Farm.objects.create(name="Test Nakuru Farm", location="Nakuru")
            print(f"✅ Created farm: {nakuru_farm.name}")
    except Exception as e:
        print(f"❌ Farm error: {e}")
        nakuru_farm = Farm.objects.create(name="Debug Farm", location="Test Location")
        print(f"✅ Created farm: {nakuru_farm.name}")
    
    # Test 1: Create a cow
    print("\n🐄 Testing Cow Creation...")
    client.force_authenticate(user=admin_user)
    cow_response = client.post('/api/cows/', {
        'farm': nakuru_farm.id,
        'name': 'Debug Cow',
        'stage': 'lactating',
        'birth_date': '2021-01-01'
    })
    print(f"Status: {cow_response.status_code}")
    if cow_response.status_code != 201:
        print(f"Error: {cow_response.json()}")
        return
    
    cow_id = cow_response.json()['id']
    print(f"✅ Created cow with ID: {cow_id}")
    
    # Test 2: Milk production
    print("\n🥛 Testing Milk Production...")
    milk_response = client.post('/api/milk-production/', {
        'cow': cow_id,
        'date': str(date.today()),
        'session': 'morning',
        'quantity': '15.50'
    })
    print(f"Status: {milk_response.status_code}")
    print(f"Response: {milk_response.json()}")
    
    # Test 3: Milk sales
    print("\n💰 Testing Milk Sales...")
    sales_response = client.post('/api/milk-sales/', {
        'farm': nakuru_farm.id,
        'date': str(date.today()),
        'quantity_sold': '50.00',
        'price_per_liter': '45.00',
        'total_amount': '2250.00'
    })
    print(f"Status: {sales_response.status_code}")
    print(f"Response: {sales_response.json()}")
    
    # Test 4: Feed creation
    print("\n🌾 Testing Feed Creation...")
    feed_response = client.post('/api/feeds/', {
        'farm': nakuru_farm.id,
        'feed_type': 'dairy_meal',
        'quantity_purchased': '100.00',
        'quantity_remaining': '100.00',
        'unit_price': '50.00',
        'transport_cost': '500.00',
        'purchase_date': str(date.today())
    })
    print(f"Status: {feed_response.status_code}")
    print(f"Response: {feed_response.json()}")
    
    if feed_response.status_code == 201:
        feed_id = feed_response.json()['id']
        
        # Test 5: Feed consumption
        print("\n🍽️ Testing Feed Consumption...")
        consumption_response = client.post('/api/feed-consumption/', {
            'cow': cow_id,
            'feed': feed_id,
            'date': str(date.today()),
            'quantity_consumed': '5.00'
        })
        print(f"Status: {consumption_response.status_code}")
        print(f"Response: {consumption_response.json()}")
    
    # Test 6: Health records
    print("\n🏥 Testing Health Records...")
    health_response = client.post('/api/health-records/', {
        'cow': cow_id,
        'date_sick': str(date.today()),
        'disease_name': 'Mastitis',
        'date_treated': str(date.today()),
        'medicine_used': 'Antibiotics',
        'medicine_cost': '500.00',
        'vet_name': 'Dr. Smith',
        'vet_contact': '+254712345678',
        'notes': 'Test health record'
    })
    print(f"Status: {health_response.status_code}")
    print(f"Response: {health_response.json()}")
    
    print("\n" + "=" * 50)
    print("🎯 DEBUGGING COMPLETE!")

if __name__ == "__main__":
    debug_specific_endpoints()