from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from .serializers import *
import secrets
import string

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'redirect': 'farm_selection' if user.is_admin else 'farm_dashboard'
            })
        return Response({'error': 'Invalid credentials'}, status=400)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Farm.objects.all()
        return Farm.objects.filter(id=self.request.user.assigned_farm_id)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

class CowViewSet(viewsets.ModelViewSet):
    queryset = Cow.objects.all()
    serializer_class = CowSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Cow.objects.all()
        return Cow.objects.filter(farm=self.request.user.assigned_farm)
    
    @action(detail=True, methods=['post'])
    def add_calf(self, request, pk=None):
        mother = self.get_object()
        calf_data = request.data.copy()
        calf_data['mother'] = mother.id
        calf_data['farm'] = mother.farm.id
        serializer = CowSerializer(data=calf_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ChickenBatchViewSet(viewsets.ModelViewSet):
    queryset = ChickenBatch.objects.all()
    serializer_class = ChickenBatchSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return ChickenBatch.objects.all()
        return ChickenBatch.objects.filter(farm=self.request.user.assigned_farm)
    
    @action(detail=True, methods=['post'])
    def update_mortality(self, request, pk=None):
        batch = self.get_object()
        deaths = int(request.data.get('deaths', 0))
        batch.current_count = max(0, batch.current_count - deaths)
        batch.save()
        return Response({'current_count': batch.current_count})
    
    @action(detail=True, methods=['post'])
    def add_hatched(self, request, pk=None):
        batch = self.get_object()
        hatched = int(request.data.get('hatched', 0))
        batch.current_count += hatched
        batch.save()
        return Response({'current_count': batch.current_count})

class MilkProductionViewSet(viewsets.ModelViewSet):
    queryset = MilkProduction.objects.all()
    serializer_class = MilkProductionSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return MilkProduction.objects.all()
        return MilkProduction.objects.filter(cow__farm=self.request.user.assigned_farm)
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class MilkSaleViewSet(viewsets.ModelViewSet):
    queryset = MilkSale.objects.all()
    serializer_class = MilkSaleSerializer
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return MilkSale.objects.none()
        return MilkSale.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Feed.objects.all()
        return Feed.objects.filter(farm=self.request.user.assigned_farm)

class FeedConsumptionViewSet(viewsets.ModelViewSet):
    queryset = FeedConsumption.objects.all()
    serializer_class = FeedConsumptionSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return FeedConsumption.objects.all()
        return FeedConsumption.objects.filter(cow__farm=self.request.user.assigned_farm)
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return HealthRecord.objects.none()
        return HealthRecord.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class EggProductionViewSet(viewsets.ModelViewSet):
    queryset = EggProduction.objects.all()
    serializer_class = EggProductionSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return EggProduction.objects.all()
        return EggProduction.objects.filter(batch__farm=self.request.user.assigned_farm)
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class ChickenFeedViewSet(viewsets.ModelViewSet):
    queryset = ChickenFeed.objects.all()
    serializer_class = ChickenFeedSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return ChickenFeed.objects.all()
        return ChickenFeed.objects.filter(farm=self.request.user.assigned_farm)

class RestockAlertViewSet(viewsets.ModelViewSet):
    queryset = RestockAlert.objects.all()
    serializer_class = RestockAlertSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return RestockAlert.objects.all()
        return RestockAlert.objects.filter(farm=self.request.user.assigned_farm)

class InviteFarmerView(APIView):
    def post(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Admin access required'}, status=403)
        
        email = request.data.get('email')
        farm_id = request.data.get('farm_id')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
            assigned_farm_id=farm_id
        )
        
        try:
            send_mail(
                'Dairy Farm App Invitation',
                f'You have been invited to join the dairy farm management system.\n\n'
                f'Login credentials:\nUsername: {email}\nPassword: {password}\n\n'
                f'Please change your password after first login.',
                'admin@dairyfarm.com',
                [email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
            pass
        
        return Response({'message': 'Farmer invited successfully'})

class MarkFeedCompleteView(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id')
        feed_type = request.data.get('feed_type', 'cow_feed')
        
        if feed_type == 'cow_feed':
            feed = Feed.objects.get(id=feed_id)
            feed.is_finished = True
            feed.needs_restock = True
            feed.save()
            
            alert = RestockAlert.objects.create(
                farm=feed.farm,
                alert_type='cow_feed',
                item_name=feed.get_feed_type_display(),
                message=f'{feed.get_feed_type_display()} is finished and needs restocking at {feed.farm.name}',
                created_by=request.user
            )
        else:
            feed = ChickenFeed.objects.get(id=feed_id)
            feed.is_finished = True
            feed.needs_restock = True
            feed.save()
            
            alert = RestockAlert.objects.create(
                farm=feed.farm,
                alert_type='chicken_feed',
                item_name=feed.feed_name,
                message=f'{feed.feed_name} is finished and needs restocking at {feed.farm.name}',
                created_by=request.user
            )
        
        alert.send_alert_email()
        return Response({'message': 'Feed marked as complete and alert sent'})

class MilkStatsView(APIView):
    def get(self, request, farm_id):
        period = request.GET.get('period', 'daily')
        
        if period == 'daily':
            stats = MilkProduction.objects.filter(
                cow__farm_id=farm_id,
                date=timezone.now().date()
            ).aggregate(
                total=Sum('quantity'),
                count=Count('id')
            )
        elif period == 'weekly':
            week_start = timezone.now().date() - timedelta(days=7)
            stats = MilkProduction.objects.filter(
                cow__farm_id=farm_id,
                date__gte=week_start
            ).aggregate(
                total=Sum('quantity'),
                count=Count('id')
            )
        elif period == 'monthly':
            month_start = timezone.now().date().replace(day=1)
            stats = MilkProduction.objects.filter(
                cow__farm_id=farm_id,
                date__gte=month_start
            ).aggregate(
                total=Sum('quantity'),
                count=Count('id')
            )
        elif period == 'yearly':
            year_start = timezone.now().date().replace(month=1, day=1)
            stats = MilkProduction.objects.filter(
                cow__farm_id=farm_id,
                date__gte=year_start
            ).aggregate(
                total=Sum('quantity'),
                count=Count('id')
            )
        
        return Response(stats)

class EggStatsView(APIView):
    def get(self, request, farm_id):
        period = request.GET.get('period', 'daily')
        
        if period == 'daily':
            stats = EggProduction.objects.filter(
                batch__farm_id=farm_id,
                date=timezone.now().date()
            ).aggregate(
                total=Sum('eggs_collected'),
                count=Count('id')
            )
        elif period == 'weekly':
            week_start = timezone.now().date() - timedelta(days=7)
            stats = EggProduction.objects.filter(
                batch__farm_id=farm_id,
                date__gte=week_start
            ).aggregate(
                total=Sum('eggs_collected'),
                count=Count('id')
            )
        elif period == 'monthly':
            month_start = timezone.now().date().replace(day=1)
            stats = EggProduction.objects.filter(
                batch__farm_id=farm_id,
                date__gte=month_start
            ).aggregate(
                total=Sum('eggs_collected'),
                count=Count('id')
            )
        elif period == 'yearly':
            year_start = timezone.now().date().replace(month=1, day=1)
            stats = EggProduction.objects.filter(
                batch__farm_id=farm_id,
                date__gte=year_start
            ).aggregate(
                total=Sum('eggs_collected'),
                count=Count('id')
            )
        
        return Response(stats)