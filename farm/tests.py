from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal
from .models import *
import json

User = get_user_model()

class DairyFarmTestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        print("\n🚀 Setting up test data...")
        
        # Create farms
        self.nakuru_farm = Farm.objects.create(name="Nakuru Farm", location="Nakuru")
        self.kisii_farm = Farm.objects.create(name="Kisii Farm", location="Kisii")
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            is_admin=True,
            first_name='Admin',
            last_name='User'
        )
        
        # Create farmers
        self.farmer1 = User.objects.create_user(
            username='farmer1@test.com',
            email='farmer1@test.com',
            password='testpass123',
            assigned_farm=self.nakuru_farm,
            first_name='John',
            last_name='Farmer'
        )
        
        self.farmer2 = User.objects.create_user(
            username='farmer2@test.com',
            email='farmer2@test.com',
            password='testpass123',
            assigned_farm=self.kisii_farm,
            first_name='Jane',
            last_name='Farmer'
        )
        
        print(f"✅ Created farms: {self.nakuru_farm.name}, {self.kisii_farm.name}")
        print(f"✅ Created users: Admin, Farmer1 (Nakuru), Farmer2 (Kisii)")

    def test_01_authentication_and_authorization(self):
        """Test login functionality and user permissions"""
        print("\n🔐 Testing Authentication & Authorization...")
        
        # Test admin login
        response = self.client.post('/api/auth/login/', {
            'username': 'admin@test.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        admin_data = response.json()
        self.assertEqual(admin_data['redirect'], 'farm_selection')
        self.assertTrue(admin_data['user']['is_admin'])
        print(f"✅ Admin login successful: {admin_data['user']['username']}")
        
        # Test farmer login
        response = self.client.post('/api/auth/login/', {
            'username': 'farmer1@test.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        farmer_data = response.json()
        self.assertEqual(farmer_data['redirect'], 'farm_dashboard')
        self.assertFalse(farmer_data['user']['is_admin'])
        print(f"✅ Farmer login successful: {farmer_data['user']['username']}")
        
        # Test invalid login
        response = self.client.post('/api/auth/login/', {
            'username': 'invalid@test.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid login properly rejected")

    def test_02_farm_management(self):
        """Test farm creation and access control"""
        print("\n🏡 Testing Farm Management...")
        
        # Login as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Test farm creation
        response = self.client.post('/api/farms/', {
            'name': 'Test Farm',
            'location': 'Eldoret'
        })
        self.assertEqual(response.status_code, 201)
        print(f"✅ Admin can create farms: {response.json()['name']}")
        
        # Test admin can see all farms
        response = self.client.get('/api/farms/')
        self.assertEqual(response.status_code, 200)
        farms = response.json()
        self.assertGreaterEqual(len(farms), 3)  # At least our 3 farms
        print(f"✅ Admin can see all farms: {len(farms)} farms")
        
        # Test farmer can only see assigned farm
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.get('/api/farms/')
        self.assertEqual(response.status_code, 200)
        farms = response.json()
        self.assertEqual(len(farms), 1)
        self.assertEqual(farms[0]['id'], self.nakuru_farm.id)
        print(f"✅ Farmer can only see assigned farm: {farms[0]['name']}")

    def test_03_cow_management_and_calf_creation(self):
        """Test cow creation, profiles, and automatic calf creation"""
        print("\n🐄 Testing Cow Management & Calf Creation...")
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Create mother cow
        cow_data = {
            'farm': self.nakuru_farm.id,
            'name': 'Bessie',
            'stage': 'lactating',
            'birth_date': '2020-01-15',
            'notes': 'High milk producer'
        }
        response = self.client.post('/api/cows/', cow_data)
        self.assertEqual(response.status_code, 201)
        mother_cow = response.json()
        print(f"✅ Created mother cow: {mother_cow['name']}")
        
        # Add calf to mother
        calf_data = {
            'name': 'Bessie Jr',
            'stage': 'calf',
            'birth_date': '2024-06-01',
            'notes': 'Healthy calf'
        }
        response = self.client.post(f'/api/cows/{mother_cow["id"]}/add_calf/', calf_data)
        self.assertEqual(response.status_code, 200)
        calf = response.json()
        self.assertEqual(calf['mother'], mother_cow['id'])
        print(f"✅ Created calf: {calf['name']} with mother: {mother_cow['name']}")
        
        # Test cow profile with calves
        response = self.client.get(f'/api/cows/{mother_cow["id"]}/')
        cow_profile = response.json()
        self.assertGreater(len(cow_profile['calves']), 0)
        print(f"✅ Mother cow profile shows calves: {cow_profile['calves']}")

    def test_04_milk_production_and_stats(self):
        """Test milk production recording and statistics"""
        print("\n🥛 Testing Milk Production & Statistics...")
        
        self.client.force_authenticate(user=self.farmer1)
        
        # Create a cow first
        self.client.force_authenticate(user=self.admin_user)
        cow_response = self.client.post('/api/cows/', {
            'farm': self.nakuru_farm.id,
            'name': 'Milky',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        cow_id = cow_response.json()['id']
        
        # Switch back to farmer to record milk
        self.client.force_authenticate(user=self.farmer1)
        
        # Record milk production for all three sessions
        sessions = ['morning', 'afternoon', 'evening']
        quantities = [15.5, 12.0, 10.5]
        
        for session, quantity in zip(sessions, quantities):
            response = self.client.post('/api/milk-production/', {
                'cow': cow_id,
                'date': str(date.today()),
                'session': session,
                'quantity': quantity
            })
            self.assertEqual(response.status_code, 201)
            print(f"✅ Recorded {session} milk: {quantity}L")
        
        # Test milk statistics
        response = self.client.get(f'/api/stats/milk/{self.nakuru_farm.id}/?period=daily')
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        expected_total = sum(quantities)
        self.assertEqual(float(stats['total']), expected_total)
        print(f"✅ Daily milk stats: {stats['total']}L total")
        
        # Test weekly stats
        response = self.client.get(f'/api/stats/milk/{self.nakuru_farm.id}/?period=weekly')
        self.assertEqual(response.status_code, 200)
        print(f"✅ Weekly milk stats: {response.json()}")

    def test_05_milk_sales_admin_only(self):
        """Test milk sales (admin only feature)"""
        print("\n💰 Testing Milk Sales (Admin Only)...")
        
        # Test farmer cannot access milk sales
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.get('/api/milk-sales/')
        sales = response.json()
        self.assertEqual(len(sales), 0)  # Farmer gets empty queryset
        print("✅ Farmer cannot see milk sales")
        
        # Test admin can record milk sales
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/milk-sales/', {
            'farm': self.nakuru_farm.id,
            'date': str(date.today()),
            'quantity_sold': 50.0,
            'price_per_liter': 45.0,
            'total_amount': 2250.0
        })
        self.assertEqual(response.status_code, 201)
        sale = response.json()
        print(f"✅ Admin recorded milk sale: {sale['quantity_sold']}L at {sale['price_per_liter']}/L")

    def test_06_feed_management_and_alerts(self):
        """Test feed management, consumption tracking, and restock alerts"""
        print("\n🌾 Testing Feed Management & Restock Alerts...")
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Create feed
        feed_response = self.client.post('/api/feeds/', {
            'farm': self.nakuru_farm.id,
            'feed_type': 'dairy_meal',
            'quantity_purchased': 100.0,
            'quantity_remaining': 100.0,
            'unit_price': 50.0,
            'transport_cost': 500.0,
            'purchase_date': str(date.today())
        })
        self.assertEqual(feed_response.status_code, 201)
        feed = feed_response.json()
        print(f"✅ Created feed: {feed['feed_type']} - {feed['quantity_purchased']}kg")
        
        # Create cow for feed consumption
        cow_response = self.client.post('/api/cows/', {
            'farm': self.nakuru_farm.id,
            'name': 'Hungry Cow',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        cow_id = cow_response.json()['id']
        
        # Record feed consumption
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.post('/api/feed-consumption/', {
            'cow': cow_id,
            'feed': feed['id'],
            'date': str(date.today()),
            'quantity_consumed': 5.0
        })
        self.assertEqual(response.status_code, 201)
        print("✅ Farmer recorded feed consumption: 5kg")
        
        # Test marking feed as complete (triggers alert)
        response = self.client.post('/api/mark-feed-complete/', {
            'feed_id': feed['id'],
            'feed_type': 'cow_feed'
        })
        self.assertEqual(response.status_code, 200)
        print("✅ Feed marked as complete - alert should be sent")
        
        # Check if alert was created
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/restock-alerts/')
        alerts = response.json()
        self.assertGreater(len(alerts), 0)
        print(f"✅ Restock alert created: {alerts[0]['message']}")

    def test_07_health_records_admin_only(self):
        """Test health records (admin only feature)"""
        print("\n🏥 Testing Health Records (Admin Only)...")
        
        # Create cow first
        self.client.force_authenticate(user=self.admin_user)
        cow_response = self.client.post('/api/cows/', {
            'farm': self.nakuru_farm.id,
            'name': 'Sick Cow',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        cow_id = cow_response.json()['id']
        
        # Test farmer cannot access health records
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.get('/api/health-records/')
        records = response.json()
        self.assertEqual(len(records), 0)  # Farmer gets empty queryset
        print("✅ Farmer cannot access health records")
        
        # Test admin can create health records
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/health-records/', {
            'cow': cow_id,
            'date_sick': str(date.today() - timedelta(days=2)),
            'disease_name': 'Mastitis',
            'date_treated': str(date.today()),
            'medicine_used': 'Antibiotics',
            'medicine_cost': 500.0,
            'vet_name': 'Dr. Smith',
            'vet_contact': '+254712345678',
            'notes': 'Responded well to treatment'
        })
        self.assertEqual(response.status_code, 201)
        health_record = response.json()
        print(f"✅ Admin created health record: {health_record['disease_name']} treated with {health_record['medicine_used']}")

    def test_08_chicken_management(self):
        """Test chicken batch management, mortality, and hatching"""
        print("\n🐔 Testing Chicken Management...")
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Create chicken batch
        response = self.client.post('/api/chicken-batches/', {
            'farm': self.nakuru_farm.id,
            'batch_name': 'Broiler Batch 1',
            'batch_number': 1,
            'initial_count': 100,
            'current_count': 100,
            'purchase_date': str(date.today() - timedelta(days=30))
        })
        self.assertEqual(response.status_code, 201)
        batch = response.json()
        print(f"✅ Created chicken batch: {batch['batch_name']} with {batch['initial_count']} chickens")
        
        # Test mortality update
        response = self.client.post(f'/api/chicken-batches/{batch["id"]}/update_mortality/', {
            'deaths': 10
        })
        self.assertEqual(response.status_code, 200)
        updated_count = response.json()['current_count']
        self.assertEqual(updated_count, 90)
        print(f"✅ Updated mortality: 10 deaths, current count: {updated_count}")
        
        # Test adding hatched chicks
        response = self.client.post(f'/api/chicken-batches/{batch["id"]}/add_hatched/', {
            'hatched': 15
        })
        self.assertEqual(response.status_code, 200)
        updated_count = response.json()['current_count']
        self.assertEqual(updated_count, 105)
        print(f"✅ Added hatched chicks: 15 hatched, current count: {updated_count}")

    def test_09_egg_production_and_stats(self):
        """Test egg production recording and statistics"""
        print("\n🥚 Testing Egg Production & Statistics...")
        
        # Create chicken batch first
        self.client.force_authenticate(user=self.admin_user)
        batch_response = self.client.post('/api/chicken-batches/', {
            'farm': self.nakuru_farm.id,
            'batch_name': 'Layer Batch 1',
            'batch_number': 2,
            'initial_count': 50,
            'current_count': 50,
            'purchase_date': str(date.today() - timedelta(days=60))
        })
        batch_id = batch_response.json()['id']
        
        # Record egg production
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.post('/api/egg-production/', {
            'batch': batch_id,
            'date': str(date.today()),
            'eggs_collected': 35
        })
        self.assertEqual(response.status_code, 201)
        egg_record = response.json()
        print(f"✅ Recorded egg production: {egg_record['eggs_collected']} eggs")
        
        # Test egg statistics
        response = self.client.get(f'/api/stats/eggs/{self.nakuru_farm.id}/?period=daily')
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        self.assertEqual(stats['total'], 35)
        print(f"✅ Daily egg stats: {stats['total']} eggs")

    def test_10_chicken_feed_management(self):
        """Test chicken feed management"""
        print("\n🌽 Testing Chicken Feed Management...")
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Create chicken feed
        response = self.client.post('/api/chicken-feeds/', {
            'farm': self.nakuru_farm.id,
            'feed_name': 'Layer Mash',
            'quantity_purchased': 200.0,
            'quantity_remaining': 200.0,
            'cost': 8000.0,
            'purchase_date': str(date.today())
        })
        self.assertEqual(response.status_code, 201)
        chicken_feed = response.json()
        print(f"✅ Created chicken feed: {chicken_feed['feed_name']} - {chicken_feed['quantity_purchased']}kg")
        
        # Test marking chicken feed as complete
        self.client.force_authenticate(user=self.farmer1)
        response = self.client.post('/api/mark-feed-complete/', {
            'feed_id': chicken_feed['id'],
            'feed_type': 'chicken_feed'
        })
        self.assertEqual(response.status_code, 200)
        print("✅ Chicken feed marked as complete")

    def test_11_farmer_invitation_system(self):
        """Test admin inviting farmers"""
        print("\n📧 Testing Farmer Invitation System...")
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Test farmer invitation
        response = self.client.post('/api/invite-farmer/', {
            'email': 'newfarmer@test.com',
            'farm_id': self.kisii_farm.id,
            'first_name': 'New',
            'last_name': 'Farmer'
        })
        self.assertEqual(response.status_code, 200)
        print("✅ Admin invited new farmer")
        
        # Check if user was created
        new_user = User.objects.get(email='newfarmer@test.com')
        self.assertEqual(new_user.assigned_farm, self.kisii_farm)
        self.assertFalse(new_user.is_admin)
        print(f"✅ New farmer created and assigned to: {new_user.assigned_farm.name}")

    def test_12_permission_boundaries(self):
        """Test that farmers cannot access other farms' data"""
        print("\n🔒 Testing Permission Boundaries...")
        
        # Create cow in Kisii farm
        self.client.force_authenticate(user=self.admin_user)
        kisii_cow_response = self.client.post('/api/cows/', {
            'farm': self.kisii_farm.id,
            'name': 'Kisii Cow',
            'stage': 'lactating',
            'birth_date': '2021-01-01'
        })
        kisii_cow_id = kisii_cow_response.json()['id']
        
        # Nakuru farmer tries to access Kisii cow
        self.client.force_authenticate(user=self.farmer1)  # Nakuru farmer
        response = self.client.get(f'/api/cows/{kisii_cow_id}/')
        self.assertEqual(response.status_code, 404)  # Should not find it
        print("✅ Nakuru farmer cannot access Kisii farm cow")
        
        # Nakuru farmer can only see Nakuru cows
        response = self.client.get('/api/cows/')
        cows = response.json()
        for cow in cows:
            self.assertEqual(cow['farm'], self.nakuru_farm.id)
        print(f"✅ Nakuru farmer only sees Nakuru cows: {len(cows)} cows")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 STARTING COMPREHENSIVE DAIRY FARM SYSTEM TESTS")
        print("=" * 60)
        
        try:
            self.test_01_authentication_and_authorization()
            self.test_02_farm_management()
            self.test_03_cow_management_and_calf_creation()
            self.test_04_milk_production_and_stats()
            self.test_05_milk_sales_admin_only()
            self.test_06_feed_management_and_alerts()
            self.test_07_health_records_admin_only()
            self.test_08_chicken_management()
            self.test_09_egg_production_and_stats()
            self.test_10_chicken_feed_management()
            self.test_11_farmer_invitation_system()
            self.test_12_permission_boundaries()
            
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED! SYSTEM IS FULLY FUNCTIONAL!")
            print("✅ Authentication & Authorization")
            print("✅ Farm Management")
            print("✅ Cow Management & Calf Creation")
            print("✅ Milk Production & Statistics")
            print("✅ Milk Sales (Admin Only)")
            print("✅ Feed Management & Alerts")
            print("✅ Health Records (Admin Only)")
            print("✅ Chicken Management")
            print("✅ Egg Production & Statistics")
            print("✅ Chicken Feed Management")
            print("✅ Farmer Invitation System")
            print("✅ Permission Boundaries")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            raise


# Simple test runner function
def run_comprehensive_test():
    """Function to run the comprehensive test"""
    test_instance = DairyFarmTestCase()
    test_instance.setUp()
    test_instance.run_all_tests()