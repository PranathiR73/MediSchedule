import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Appointment, Patient, Schedule


PHONE_PATTERN = re.compile(r'^\+?[0-9]{10,15}$')


class PatientRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise ValidationError('A patient with this email already exists.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip()
        if not PHONE_PATTERN.match(phone):
            raise ValidationError('Enter a valid phone number with 10 to 15 digits.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords must match.')
        return cleaned_data

    def save(self):
        full_name = self.cleaned_data['full_name'].strip()
        first_name, _, last_name = full_name.partition(' ')
        email = self.cleaned_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        return Patient.objects.create(user=user, phone_number=self.cleaned_data['phone_number'])


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email address')


class BookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason_for_visit']
        widgets = {
            'reason_for_visit': forms.Textarea(attrs={'rows': 4}),
        }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['appointment_date', 'appointment_time', 'is_booked']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
