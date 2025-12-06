from django.db import models
from django.contrib.auth.models import User
from phonenumbers import parse, is_valid_number
from django.core.exceptions import ValidationError
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
import uuid
# Create your models here.


def validate_nigerian_phone(value):
    try:
        phone = parse(value, "NG")
        if not is_valid_number(phone):
            return ValidationError("enter a Valid Nigerian number")
        
    except:
        return ValidationError("Invalid phone number format ")
    



# Student model

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, validators=[validate_nigerian_phone])
    matric_number = models.CharField(max_length=20, unique=True)
    school = models.CharField(max_length=100, default="Federal University of Technology Minna")
    is_verified_student = models.BooleanField(default=False)


    # Referral system
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    referral_count = models.IntegerField(default=0)
    free_trips = models.IntegerField(default=0)  # How many free trips earned
    
    date_joined = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:8].upper()
        # Give free trip every 5 referrals
        if self.referral_count >= 5 and self.referral_count % 5 == 0:
            if (self.referral_count // 5) > (self.free_trips):
                self.free_trips += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matric_number})"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, validators=[validate_nigerian_phone])
    driver_id = models.CharField(max_length=15, unique=True, blank=True)  # DRV-NGR-0001
    license_number = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='drivers/')
    is_approved = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.driver_id:
            last = Driver.objects.all().order_by('id').last()
            num = last.id + 1 if last else 1
            self.driver_id = f"ARl-NGR-{num:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.driver_id}"
    

# 3. TRIP MODEL (Only from FUT Minna at launch)
class Trip(models.Model):
    trip_code = models.CharField(max_length=20, unique=True)
    destination = models.CharField(max_length=100)
    departure_date = models.DateTimeField()
    price_student = models.DecimalField(max_digits=10, decimal_places=0, default=4000)
    price_regular = models.DecimalField(max_digits=10, decimal_places=0, default=18000)
    bus_capacity = models.IntegerField(default=14)
    passengers_boarded = models.IntegerField(default=0)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.trip_code:
            self.trip_code = f"TRIP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.trip_code} → {self.destination}"
    


# 5. REGULAR PASSENGER (Non-student users)
class RegularPassenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, validators=[validate_nigerian_phone])
    full_name = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} (Regular Passenger)"
    
class Booking(models.Model):
    BOOKED_BY_CHOICES = [
        ('student', 'Student'),
        ('regular', 'Regular Passenger'),
    ]
    
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.CASCADE)
    regular_passenger = models.ForeignKey(RegularPassenger, null=True, blank=True, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    booking_code = models.CharField(max_length=10, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    used_free_trip = models.BooleanField(default=False)
    is_boarded = models.BooleanField(default=False)
    booked_by = models.CharField(max_length=10, choices=BOOKED_BY_CHOICES)
    booked_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = uuid.uuid4().hex[:8].upper()

        # Set amount based on who booked
        if self.student:
            self.amount_paid = 0 if self.used_free_trip else self.trip.price_student
            self.booked_by = 'student'
        else:
            self.amount_paid = self.trip.price_regular
            self.booked_by = 'regular'

        # Generate QR code
        if not self.qr_code:
            name = "Passenger"
            if self.student:
                name = self.student.user.get_full_name() or self.student.user.email
            elif self.regular_passenger:
                name = self.regular_passenger.full_name

            qr_data = f"BOOKING:{self.booking_code}|TRIP:{self.trip.trip_code}|NAME:{name}"
            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            filename = f"qr_{self.booking_code}.png"
            self.qr_code.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        name = "Unknown"
        if self.student:
            name = self.student.user.get_full_name()
        elif self.regular_passenger:
            name = self.regular_passenger.full_name
        return f"{name} → {self.trip.destination}"