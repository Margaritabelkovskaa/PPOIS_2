from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rooms/', views.rooms, name='rooms'),
    path('devices/', views.devices, name='devices'),
    path('security/', views.security, name='security'),
    path('owner/', views.owner, name='owner'),
    path('automation/', views.automation, name='automation'),

    # Базовые API
    path('api/device/', views.api_add_device, name='api_add_device'),
    path('api/device/<str:device_id>/toggle/', views.api_toggle_device, name='api_toggle_device'),
    path('api/device/<str:device_id>/', views.api_delete_device, name='api_delete_device'),

    # Освещение
    path('api/device/<str:device_id>/brightness/', views.api_set_brightness, name='api_set_brightness'),

    # Климат
    path('api/device/<str:device_id>/temperature/', views.api_set_temperature, name='api_set_temperature'),
    path('api/device/<str:device_id>/humidity/', views.api_set_humidity, name='api_set_humidity'),
    path('api/device/<str:device_id>/mode/', views.api_set_mode, name='api_set_mode'),
    path('api/device/<str:device_id>/fan_speed/', views.api_set_fan_speed, name='api_set_fan_speed'),

    # Чайник
    path('api/device/<str:device_id>/boil/', views.api_boil_kettle, name='api_boil_kettle'),
    path('api/device/<str:device_id>/kettle_temperature/', views.api_set_kettle_temperature,
         name='api_set_kettle_temperature'),

    # Пылесос
    path('api/device/<str:device_id>/start_cleaning/', views.api_start_cleaning, name='api_start_cleaning'),
    path('api/device/<str:device_id>/stop_cleaning/', views.api_stop_cleaning, name='api_stop_cleaning'),
    path('api/device/<str:device_id>/cleaner_mode/', views.api_set_cleaner_mode, name='api_set_cleaner_mode'),

    # Безопасность
    path('api/security/arm/', views.api_arm_security, name='api_arm_security'),
    path('api/security/disarm/', views.api_disarm_security, name='api_disarm_security'),
    path('api/security/trigger/', views.api_trigger_alarm, name='api_trigger_alarm'),

    # Устройство хозяина
    path('api/owner/connect/', views.api_owner_connect, name='api_owner_connect'),
    path('api/owner/disconnect/', views.api_owner_disconnect, name='api_owner_disconnect'),
    path('api/owner/notify/', views.api_owner_notify, name='api_owner_notify'),
    path('api/owner/clear_history/', views.api_clear_history, name='api_clear_history'),
    # Автоматизация
    path('api/automation/add/', views.api_add_automation, name='api_add_automation'),
    path('api/automation/<str:rule_id>/toggle/', views.api_toggle_automation, name='api_toggle_automation'),
    path('api/automation/<str:rule_id>/delete/', views.api_delete_automation, name='api_delete_automation'),
    path('api/devices/', views.api_get_devices, name='api_get_devices'),
]