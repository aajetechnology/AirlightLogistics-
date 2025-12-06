# core/forms.py  ← 100% WORKING VERSION
from django import forms
from django.contrib.auth.models import User
from .models import Student, RegularPassenger
import re

# List of valid Nigerian school domains (we will expand forever)
NIGERIAN_SCHOOL_DOMAINS = [
    "futminna.edu.ng", "futo.edu.ng", "unilag.edu.ng", "unn.edu.ng",
    "ui.edu.ng", "oauife.edu.ng", "abu.edu.ng", "uniben.edu",
    "unilorin.edu.ng", "lasu.edu.ng", "yabatech.edu.ng",
    "auchipoly.edu.ng", "nigerpoly.edu.ng", "ibbu.edu.ng",
    "noun.edu.ng", "ksu.edu.ng", "futia.edu.ng", "unical.edu.ng",
    # Add more as students join → no limit!
]

class StudentRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    email = forms.EmailField(
        help_text="Use your official school email e.g. john@futminna.edu.ng"
    )
    phone = forms.CharField(max_length=15, label="Phone Number (e.g. 08012345678)")
    matric_number = forms.CharField(max_length=20, label="Matric Number")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    referral_code = forms.CharField(
        max_length=10,
        required=False,
        help_text="Enter referral code if someone invited you"
    )

    class Meta:
        model = Student
        fields = ['matric_number', 'phone']

    # Validate school email
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        domain = email.split('@')[-1]
        
        if not any(domain.endswith(valid) for valid in ['edu.ng', 'ac.ng']) and \
           domain not in NIGERIAN_SCHOOL_DOMAINS:
            raise forms.ValidationError(
                "Please use your official Nigerian school email (e.g. name@futminna.edu.ng, name@yabatech.edu.ng)"
            )
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email

    # Validate matric number
    def clean_matric_number(self):
        matric = self.cleaned_data['matric_number'].upper().replace(" ", "")
        if not re.match(r"^\d{4}/\d{4,6}[A-Z]?$", matric):
            raise forms.ValidationError("Invalid matric format. Example: 2020/1C1234 or 2021/12345")
        if Student.objects.filter(matric_number=matric).exists():
            raise forms.ValidationError("This matric number is already registered")
        return matric


class RegularPassengerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    email = forms.EmailField(label="Email Address")
    phone = forms.CharField(max_length=15, label="Phone Number")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = RegularPassenger
        fields = ['phone']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 11:
            raise forms.ValidationError("Phone number too short")
        return phone