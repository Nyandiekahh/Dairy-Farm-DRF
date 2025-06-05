from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'farms', views.FarmViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'cows', views.CowViewSet)
router.register(r'chicken-batches', views.ChickenBatchViewSet)
router.register(r'milk-production', views.MilkProductionViewSet)
router.register(r'milk-sales', views.MilkSaleViewSet)
router.register(r'feeds', views.FeedViewSet)
router.register(r'feed-consumption', views.FeedConsumptionViewSet)
router.register(r'health-records', views.HealthRecordViewSet)
router.register(r'egg-production', views.EggProductionViewSet)
router.register(r'chicken-feeds', views.ChickenFeedViewSet)
router.register(r'restock-alerts', views.RestockAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('stats/milk/<int:farm_id>/', views.MilkStatsView.as_view(), name='milk-stats'),
    path('stats/eggs/<int:farm_id>/', views.EggStatsView.as_view(), name='egg-stats'),
    path('invite-farmer/', views.InviteFarmerView.as_view(), name='invite-farmer'),
    path('mark-feed-complete/', views.MarkFeedCompleteView.as_view(), name='mark-feed-complete'),
]