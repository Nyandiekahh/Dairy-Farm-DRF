from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
import uuid

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    assigned_farm = models.ForeignKey('Farm', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)

class Farm(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.location}"

class Cow(models.Model):
    STAGES = [
        ('calf', 'Calf'),
        ('heifer', 'Heifer'), 
        ('pregnant', 'Pregnant'),
        ('lactating', 'Lactating'),
        ('dry', 'Dry'),
        ('heat', 'Heat'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='cows/', blank=True)
    stage = models.CharField(max_length=20, choices=STAGES, default='calf')
    mother = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    birth_date = models.DateField()
    ai_date = models.DateField(null=True, blank=True)
    estimated_birth = models.DateField(null=True, blank=True)
    actual_birth = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.farm.name}"

class ChickenBatch(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    batch_name = models.CharField(max_length=50)
    batch_number = models.PositiveIntegerField()
    initial_count = models.PositiveIntegerField()
    current_count = models.PositiveIntegerField()
    purchase_date = models.DateField()
    hatch_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['farm', 'batch_number']
    
    def __str__(self):
        return f"{self.batch_name} #{self.batch_number} - {self.farm.name}"

class MilkProduction(models.Model):
    SESSIONS = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]
    
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    date = models.DateField()
    session = models.CharField(max_length=10, choices=SESSIONS)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cow', 'date', 'session']

class MilkSale(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_sold = models.DecimalField(max_digits=8, decimal_places=2)
    price_per_liter = models.DecimalField(max_digits=6, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Feed(models.Model):
    FEED_TYPES = [
        ('dairy_meal', 'Dairy Meal'),
        ('maize_jam', 'Maize Jam'),
        ('maclic_supa', 'Maclic Supa'),
        ('maclic_plus', 'Maclic Plus'),
        ('napier_hay_silage', 'Napier/Hay/Silage'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    feed_type = models.CharField(max_length=20, choices=FEED_TYPES)
    quantity_purchased = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_remaining = models.DecimalField(max_digits=8, decimal_places=2)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    transport_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    purchase_date = models.DateField()
    is_finished = models.BooleanField(default=False)
    needs_restock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class FeedConsumption(models.Model):
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_consumed = models.DecimalField(max_digits=6, decimal_places=2)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class HealthRecord(models.Model):
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    date_sick = models.DateField()
    disease_name = models.CharField(max_length=100)
    date_treated = models.DateField()
    medicine_used = models.CharField(max_length=100)
    medicine_cost = models.DecimalField(max_digits=8, decimal_places=2)
    vet_name = models.CharField(max_length=100)
    vet_contact = models.CharField(max_length=15)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class EggProduction(models.Model):
    batch = models.ForeignKey(ChickenBatch, on_delete=models.CASCADE)
    date = models.DateField()
    eggs_collected = models.PositiveIntegerField()
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChickenFeed(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    feed_name = models.CharField(max_length=100)
    quantity_purchased = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_remaining = models.DecimalField(max_digits=8, decimal_places=2)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    purchase_date = models.DateField()
    is_finished = models.BooleanField(default=False)
    needs_restock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class RestockAlert(models.Model):
    ALERT_TYPES = [
        ('cow_feed', 'Cow Feed'),
        ('chicken_feed', 'Chicken Feed'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=15, choices=ALERT_TYPES)
    item_name = models.CharField(max_length=100)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def send_alert_email(self):
        try:
            from django.template.loader import render_to_string
            from django.utils import timezone
            
            admin_emails = User.objects.filter(is_admin=True).values_list('email', flat=True)
            
            # Create detailed email content
            subject = f'🚨 URGENT: {self.item_name} Stock Alert - {self.farm.name}'
            
            # Detailed message
            message = f"""
DAIRY FARM MANAGEMENT SYSTEM - STOCK ALERT
═══════════════════════════════════════════

🚨 URGENT RESTOCK REQUIRED 🚨

Farm: {self.farm.name} ({self.farm.location})
Item: {self.item_name}
Alert Type: {self.get_alert_type_display()}
Date/Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Reported By: {self.created_by.first_name} {self.created_by.last_name} ({self.created_by.username})

DETAILS:
{self.message}

ACTION REQUIRED:
- Contact your supplier immediately
- Update inventory once restocked
- Monitor consumption patterns

FARM CONTACT INFO:
Admin: {self.created_by.first_name} {self.created_by.last_name}
Phone: {getattr(self.created_by, 'phone', 'Not provided')}
Email: {self.created_by.email}

────────────────────────────────────────────
Dairy Farm Management System
Automated Alert #{self.id}
Generated: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
            """
            
            # HTML version for better formatting
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h2>🚨 URGENT STOCK ALERT</h2>
                    <p style="margin: 0; font-size: 18px;">Dairy Farm Management System</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
                    <h3 style="color: #dc3545; margin-top: 0;">Restock Required Immediately</h3>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #dee2e6;">Farm:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{self.farm.name} ({self.farm.location})</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #dee2e6;">Item:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6; color: #dc3545; font-weight: bold;">{self.item_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #dee2e6;">Alert Type:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{self.get_alert_type_display()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #dee2e6;">Date/Time:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #dee2e6;">Reported By:</td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{self.created_by.first_name} {self.created_by.last_name}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #dee2e6;">
                    <h4 style="color: #495057;">Details:</h4>
                    <p style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px;">{self.message}</p>
                    
                    <h4 style="color: #495057;">Action Required:</h4>
                    <ul style="color: #6c757d;">
                        <li>Contact your supplier immediately</li>
                        <li>Update inventory once restocked</li>
                        <li>Monitor consumption patterns</li>
                    </ul>
                    
                    <h4 style="color: #495057;">Farm Contact Info:</h4>
                    <p style="margin: 5px 0;"><strong>Name:</strong> {self.created_by.first_name} {self.created_by.last_name}</p>
                    <p style="margin: 5px 0;"><strong>Phone:</strong> {getattr(self.created_by, 'phone', 'Not provided')}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {self.created_by.email}</p>
                </div>
                
                <div style="background: #6c757d; color: white; padding: 15px; border-radius: 0 0 10px 10px; text-align: center; font-size: 12px;">
                    <p style="margin: 0;">Dairy Farm Management System - Automated Alert #{self.id}</p>
                    <p style="margin: 5px 0 0 0;">Generated: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </body>
            </html>
            """
            
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                html_message=html_message,
                fail_silently=True,
            )
            
            print(f"✅ Detailed restock alert sent to {len(admin_emails)} admins")
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            pass