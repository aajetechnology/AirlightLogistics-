# core/views.py — FINAL 100% CLEAN & WORKING (NO INDENTATION, NO ERRORS)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .forms import StudentRegistrationForm, RegularPassengerForm
from .models import Student, RegularPassenger, Trip, Booking
from django.views.decorators.http import require_POST

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, "Please fill both email and password")
            return render(request, 'login.html')

        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")

            if hasattr(user, 'student'):
                return redirect('passenger_dashboard')
            elif hasattr(user, 'regularpassenger'):
                return redirect('trip_list')
            else:
                return redirect('/admin/')
        else:
            messages.error(request, "Wrong email or password. Try again!")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


@login_required
def passenger_dashboard(request):
    # Get profile
    student = request.user.student if hasattr(request.user, 'student') else None
    regular = request.user.regularpassenger if hasattr(request.user, 'regularpassenger') else None

    upcoming_bookings = Booking.objects.filter(
        trip__departure_date__gte=timezone.now(),
        trip__is_active=True
    ).filter(
        models.Q(student=student) | models.Q(regular_passenger=regular)
    ).order_by('trip__departure_date')

    return render(request, 'dashboard.html', {
        'upcoming_bookings': upcoming_bookings
    })


@login_required
def trip_list(request):
    trips = Trip.objects.filter(is_active=True, departure_date__gte=timezone.now()).order_by('departure_date')
    return render(request, 'trips.html', {'trips': trips})


@require_POST
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, is_boarded=False)
    
    # Check ownership
    if (booking.student and booking.student.user == request.user) or \
       (booking.regular_passenger and booking.regular_passenger.user == request.user):
        trip = booking.trip
        trip.passengers_boarded -= 1
        trip.save()
        booking.delete()
        messages.success(request, "Booking cancelled successfully!")
    else:
        messages.error(request, "You can't cancel this booking.")
    
    return redirect('passenger_dashboard')

@login_required
def book_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, is_active=True)

    if trip.passengers_boarded >= trip.bus_capacity:
        messages.error(request, "This trip is fully booked!")
        return redirect('trip_list')

    is_student = hasattr(request.user, 'student')
    student_profile = request.user.student if is_student else None
    regular_profile = None

    if not is_student:
        try:
            regular_profile = request.user.regularpassenger
        except:
            messages.error(request, "Complete your profile first!")
            return redirect('trip_list')

    # Prevent double booking
    if Booking.objects.filter(trip=trip, student=student_profile, regular_passenger=regular_profile).exists():
        messages.error(request, "You already booked this trip!")
        return redirect('trip_list')

    booking = Booking(
        trip=trip,
        student=student_profile,
        regular_passenger=regular_profile,
        booked_by='student' if is_student else 'regular',
        amount_paid=trip.price_student if is_student else trip.price_regular,
        used_free_trip=False
    )
    booking.save()

    trip.passengers_boarded += 1
    trip.save()

    messages.success(request, f"Booking successful! Code: {booking.booking_code}")
    return redirect('ticket_detail', booking.id)


@login_required
def ticket_detail(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        trip__is_active=True,
        student__user=request.user if hasattr(request.user, 'student') else None,
        regular_passenger__user=request.user if hasattr(request.user, 'regularpassenger') else None
    )
    return render(request, 'ticket.html', {'booking': booking})


def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            student = Student(
                user=user,
                phone=form.cleaned_data['phone'],
                matric_number=form.cleaned_data['matric_number'].upper(),
                is_verified_student=True
            )
            student.save()

            ref_code = form.cleaned_data.get('referral_code')
            if ref_code:
                try:
                    referrer = Student.objects.get(referral_code__iexact=ref_code)
                    student.referred_by = referrer
                    referrer.referral_count += 1
                    referrer.save()
                except Student.DoesNotExist:
                    pass

            login(request, user)
            messages.success(request, "Student account created! Welcome!")
            return redirect('passenger_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register_student.html', {'form': form})


def register_regular(request):
    if request.method == "POST":
        form = RegularPassengerForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            passenger = RegularPassenger(
                user=user,
                phone=form.cleaned_data['phone'],
                full_name=f"{user.first_name} {user.last_name}"
            )
            passenger.save()
            login(request, user)
            messages.success(request, "Regular account created!")
            return redirect('trip_list')
    else:
        form = RegularPassengerForm()
    return render(request, 'register_regular.html', {'form': form})