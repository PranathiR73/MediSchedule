from django.contrib import admin

from .models import Appointment, Patient, Schedule


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone_number')

    @admin.display(description='Full name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('appointment_date', 'appointment_time', 'is_booked')
    list_filter = ('is_booked', 'appointment_date')
    search_fields = ('appointment_date',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'schedule', 'status', 'created_at')
    list_filter = ('status', 'schedule__appointment_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'patient__user__email')
