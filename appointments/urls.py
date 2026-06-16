from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.PatientLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('slots/', views.available_slots, name='available_slots'),
    path('slots/<int:schedule_id>/book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/schedules/', views.manage_schedules, name='manage_schedules'),
    path('staff/schedules/add/', views.schedule_form, name='add_schedule'),
    path('staff/schedules/<int:schedule_id>/edit/', views.schedule_form, name='edit_schedule'),
    path('staff/schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('staff/patients/', views.manage_patients, name='manage_patients'),
    path('staff/patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('staff/appointments/', views.manage_appointments, name='manage_appointments'),
    path('staff/appointments/<int:appointment_id>/status/', views.update_appointment_status, name='update_appointment_status'),
]
