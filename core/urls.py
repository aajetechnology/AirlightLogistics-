from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.passenger_dashboard, name='passenger_dashboard'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('trips/', views.trip_list, name='trip_list'),
    path('book/<int:trip_id>/', views.book_trip, name='book_trip'),
    path('ticket/<int:booking_id>/', views.ticket_detail, name='ticket_detail'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/regular/', views.register_regular, name='register_regular'),
]