from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import (
    AppointmentStatusForm,
    BookingForm,
    LoginForm,
    PatientRegistrationForm,
    ScheduleForm,
)
from .models import Appointment, Patient, Schedule


def is_admin(user):
    return user.is_authenticated and user.is_staff


def patient_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    return user_passes_test(is_admin, login_url='login')(view_func)


def home(request):
    return render(request, 'appointments/home.html')


def about(request):
    return render(request, 'appointments/about.html')


def contact(request):
    return render(request, 'appointments/contact.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'patient_dashboard')

    form = PatientRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        patient = form.save()
        login(request, patient.user)
        messages.success(request, 'Registration successful. Welcome to your dashboard.')
        return redirect('patient_dashboard')
    return render(request, 'appointments/register.html', {'form': form})


class PatientLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'appointments/login.html'

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('patient_dashboard')


@patient_required
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)
    today = timezone.localdate()
    upcoming = Appointment.objects.filter(
        patient=patient,
        status=Appointment.STATUS_CONFIRMED,
        schedule__appointment_date__gte=today,
    ).select_related('schedule')[:5]
    stats = {
        'upcoming': Appointment.objects.filter(
            patient=patient,
            status=Appointment.STATUS_CONFIRMED,
            schedule__appointment_date__gte=today,
        ).count(),
        'completed': Appointment.objects.filter(patient=patient, status=Appointment.STATUS_COMPLETED).count(),
        'cancelled': Appointment.objects.filter(patient=patient, status=Appointment.STATUS_CANCELLED).count(),
        'available_slots': Schedule.objects.filter(is_booked=False, appointment_date__gte=today).count(),
    }
    available_slots = Schedule.objects.filter(is_booked=False, appointment_date__gte=today)[:6]
    return render(
        request,
        'appointments/patient_dashboard.html',
        {'patient': patient, 'upcoming': upcoming, 'stats': stats, 'available_slots': available_slots},
    )


@patient_required
def available_slots(request):
    today = timezone.localdate()
    schedules = Schedule.objects.filter(is_booked=False, appointment_date__gte=today)
    return render(request, 'appointments/available_slots.html', {'schedules': schedules})


@patient_required
def book_appointment(request, schedule_id):
    patient = get_object_or_404(Patient, user=request.user)
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if schedule.is_booked:
        messages.error(request, 'That appointment slot has already been booked.')
        return redirect('available_slots')

    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                locked_schedule = Schedule.objects.select_for_update().get(pk=schedule.pk)
                has_active_appointment = Appointment.objects.filter(
                    schedule=locked_schedule,
                ).exclude(status=Appointment.STATUS_CANCELLED).exists()
                if locked_schedule.is_booked or has_active_appointment:
                    messages.error(request, 'That appointment slot was just booked. Please choose another slot.')
                    return redirect('available_slots')
                appointment = form.save(commit=False)
                appointment.patient = patient
                appointment.schedule = locked_schedule
                appointment.status = Appointment.STATUS_CONFIRMED
                appointment.save()
                locked_schedule.is_booked = True
                locked_schedule.save(update_fields=['is_booked'])
        except IntegrityError:
            messages.error(request, 'Unable to book this slot. Please try another available appointment.')
            return redirect('available_slots')

        messages.success(request, 'Appointment confirmed successfully.')
        return redirect('my_appointments')
    return render(request, 'appointments/book_appointment.html', {'form': form, 'schedule': schedule})


@patient_required
def my_appointments(request):
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).select_related('schedule')
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})


@patient_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('schedule'),
        pk=appointment_id,
        patient__user=request.user,
    )
    if request.method == 'POST':
        if appointment.status == Appointment.STATUS_CANCELLED:
            messages.info(request, 'This appointment is already cancelled.')
        else:
            appointment.status = Appointment.STATUS_CANCELLED
            appointment.save(update_fields=['status'])
            if not appointment.schedule.appointments.exclude(status=Appointment.STATUS_CANCELLED).exists():
                appointment.schedule.is_booked = False
                appointment.schedule.save(update_fields=['is_booked'])
            messages.success(request, 'Appointment cancelled and the slot is available again.')
    return redirect('my_appointments')


@admin_required
def admin_dashboard(request):
    stats = {
        'patients': Patient.objects.count(),
        'appointments': Appointment.objects.count(),
        'available_slots': Schedule.objects.filter(is_booked=False).count(),
        'booked_slots': Schedule.objects.filter(is_booked=True).count(),
    }
    recent_appointments = Appointment.objects.select_related('patient__user', 'schedule')[:6]
    return render(request, 'appointments/admin_dashboard.html', {'stats': stats, 'recent_appointments': recent_appointments})


@admin_required
def manage_schedules(request):
    schedules = Schedule.objects.all()
    return render(request, 'appointments/manage_schedules.html', {'schedules': schedules})


@admin_required
def schedule_form(request, schedule_id=None):
    schedule = get_object_or_404(Schedule, pk=schedule_id) if schedule_id else None
    form = ScheduleForm(request.POST or None, instance=schedule)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
            messages.success(request, 'Schedule saved successfully.')
            return redirect('manage_schedules')
        except IntegrityError:
            messages.error(request, 'A schedule already exists for that date and time.')
    return render(request, 'appointments/schedule_form.html', {'form': form, 'schedule': schedule})


@admin_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully.')
    return redirect('manage_schedules')


@admin_required
def manage_patients(request):
    query = request.GET.get('q', '').strip()
    patients = Patient.objects.select_related('user')
    if query:
        patients = patients.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(phone_number__icontains=query)
        )
    return render(request, 'appointments/manage_patients.html', {'patients': patients, 'query': query})


@admin_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient.objects.select_related('user'), pk=patient_id)
    appointments = patient.appointments.select_related('schedule')
    return render(request, 'appointments/patient_detail.html', {'patient': patient, 'appointments': appointments})


@admin_required
def manage_appointments(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    date = request.GET.get('date', '').strip()
    appointments = Appointment.objects.select_related('patient__user', 'schedule')

    if query:
        appointments = appointments.filter(
            Q(patient__user__first_name__icontains=query)
            | Q(patient__user__last_name__icontains=query)
            | Q(patient__user__email__icontains=query)
            | Q(reason_for_visit__icontains=query)
        )
    if status:
        appointments = appointments.filter(status=status)
    if date:
        appointments = appointments.filter(schedule__appointment_date=date)

    return render(
        request,
        'appointments/manage_appointments.html',
        {'appointments': appointments, 'query': query, 'status': status, 'date': date, 'status_choices': Appointment.STATUS_CHOICES},
    )


@admin_required
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment.objects.select_related('schedule'), pk=appointment_id)
    old_status = appointment.status
    form = AppointmentStatusForm(request.POST or None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        new_status = form.cleaned_data['status']
        if old_status == Appointment.STATUS_CANCELLED and new_status != Appointment.STATUS_CANCELLED:
            active_exists = Appointment.objects.filter(schedule=appointment.schedule).exclude(
                pk=appointment.pk,
            ).exclude(status=Appointment.STATUS_CANCELLED).exists()
            if active_exists:
                messages.error(request, 'This slot is already assigned to another active appointment.')
                return redirect('manage_appointments')
        updated = form.save()
        updated.schedule.is_booked = updated.schedule.appointments.exclude(
            status=Appointment.STATUS_CANCELLED,
        ).exists()
        updated.schedule.save(update_fields=['is_booked'])
        messages.success(request, 'Appointment status updated.')
    return redirect('manage_appointments')
