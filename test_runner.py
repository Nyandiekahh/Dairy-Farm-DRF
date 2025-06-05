#!/usr/bin/env python3
"""
Simple test runner for the dairy farm system
Run this to test all features
"""
import os
import django
from django.test.utils import get_runner
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dairy_farm.settings')
    django.setup()
    
    # Import after Django setup
    from farm.tests import DairyFarmTestCase
    
    print("🚀 STARTING DAIRY FARM SYSTEM TESTS...")
    print("This will test all features including:")
    print("• Authentication & User Management")
    print("• Farm Management")
    print("• Cow & Calf Management")
    print("• Milk Production & Statistics")
    print("• Feed Management & Alerts")
    print("• Health Records")
    print("• Chicken & Egg Management")
    print("• Permission Controls")
    print()
    
    # Run the tests
    test_instance = DairyFarmTestCase()
    test_instance.setUp()
    test_instance.run_all_tests()
