#!/usr/bin/env python3
"""
Debug script to see what's causing the 400 errors
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/home/nyandieka/Projects/dairy_farm_app')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dairy_farm.settings')
django.setup()

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from datetime import date
import json
from farm.models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class DebugTests:
    def __init__(self):
        self.client = APIClient()
        
    def setUp(self):
        # Create farms
        self.nakuru_farm = Farm.objects.create(name="Nakuru Farm", location="Nakuru")
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            is_admin=True,
            first_name='Admin',
            last_name='User'
        )
        
        # Create farmer
        self.farmer1 = User.objects.create_user(
            username='farmer1@test.com',
            email='farmer1@test.com',
            password='testpass123',
            assigned_farm=self.nakuru_farm,
            first_name='John',
            last_name='Farmer'
        )

    def debug_milk_production(self):
        print("🐄 Debugging Milk Production...")
        
        # Create cow first
        self.client.force_authenticate(user=self.admin_user)
        cow_response = self.client.post('/api/cows/', {
            'farm': self.nakuru_farm.id,
            'name': 'Milky',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        
        if cow_response.status_code != 201:
            print(f"❌ Cow creation failed: {cow_response.status_code}")
            print(f"Error: {cow_response.json()}")
            return
        
        cow_id = cow_response.json()['id']
        print(f"✅ Created cow with ID: {cow_id}")
        
        # Try to record milk production
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.post('/api/milk-production/', {
            'cow': cow_id,
            'date': str(date.today()),
            'session': 'morning',
            'quantity': 15.5
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    def debug_milk_sales(self):
        print("\n💰 Debugging Milk Sales...")
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/milk-sales/', {
            'farm': self.nakuru_farm.id,
            'date': str(date.today()),
            'quantity_sold': 50.0,
            'price_per_liter': 45.0,
            'total_amount': 2250.0
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    def debug_feed_consumption(self):
        print("\n🌾 Debugging Feed Consumption...")
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Create feed first
        feed_response = self.client.post('/api/feeds/', {
            'farm': self.nakuru_farm.id,
            'feed_type': 'dairy_meal',
            'quantity_purchased': 100.0,
            'quantity_remaining': 100.0,
            'unit_price': 50.0,
            'transport_cost': 500.0,
            'purchase_date': str(date.today())
        })
        
        if feed_response.status_code != 201:
            print(f"❌ Feed creation failed: {feed_response.status_code}")
            print(f"Error: {feed_response.json()}")
            return
            
        feed_id = feed_response.json()['id']
        print(f"✅ Created feed with ID: {feed_id}")
        
        # Create cow
        cow_response = self.client.post('/api/cows/', {
            'farm': self.nakuru_farm.id,
            'name': 'Hungry Cow',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        
        if cow_response.status_code != 201:
            print(f"❌ Cow creation failed: {cow_response.status_code}")
            print(f"Error: {cow_response.json()}")
            return
            
        cow_id = cow_response.json()['id']
        print(f"✅ Created cow with ID: {cow_id}")
        
        # Try feed consumption
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.post('/api/feed-consumption/', {
            'cow': cow_id,
            'feed': feed_id,
            'date': str(date.today()),
            'quantity_consumed': 5.0
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    def debug_health_records(self):
        print("\n🏥 Debugging Health Records...")
        
        # Create cow first
        self.client.force_authenticate(user=self.admin_user)
        cow_response = self.client.post('/api/cows/', {
            'farm': self.nakuru_farm.id,
            'name': 'Sick Cow',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        
        if cow_response.status_code != 201:
            print(f"❌ Cow creation failed: {cow_response.status_code}")
            print(f"Error: {cow_response.json()}")
            return
            
        cow_id = cow_response.json()['id']
        print(f"✅ Created cow with ID: {cow_id}")
        
        # Try health record
        response = self.client.post('/api/health-records/', {
            'cow': cow_id,
            'date_sick': str(date.today()),
            'disease_name': 'Mastitis',
            'date_treated': str(date.today()),
            'medicine_used': 'Antibiotics',
            'medicine_cost': 500.0,
            'vet_name': 'Dr. Smith',
            'vet_contact': '+254712345678',
            'notes': 'Responded well to treatment'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    def debug_egg_production(self):
        print("\n🥚 Debugging Egg Production...")
        
        # Create chicken batch first
        self.client.force_authenticate(user=self.admin_user)
        batch_response = self.client.post('/api/chicken-batches/', {
            'farm': self.nakuru_farm.id,
            'batch_name': 'Layer Batch 1',
            'batch_number': 2,
            'initial_count': 50,
            'current_count': 50,
            'purchase_date': str(date.today())
        })
        
        if batch_response.status_code != 201:
            print(f"❌ Batch creation failed: {batch_response.status_code}")
            print(f"Error: {batch_response.json()}")
            return
            
        batch_id = batch_response.json()['id']
        print(f"✅ Created batch with ID: {batch_id}")
        
        # Try egg production
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.post('/api/egg-production/', {
            'batch': batch_id,
            'date': str(date.today()),
            'eggs_collected': 35
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    def run_debug(self):
        print("🔍 DEBUGGING FAILED TESTS...")
        print("=" * 50)
        
        self.debug_milk_production()
        self.debug_milk_sales()
        self.debug_feed_consumption()
        self.debug_health_records()
        self.debug_egg_production()
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    debug = DebugTests()
    debug.setUp()
    debug.run_debug()