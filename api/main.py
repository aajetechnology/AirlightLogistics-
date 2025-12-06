# api/main.py  ← FINAL 100% WORKING DRIVER SCAN API
import os
import django
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# SETUP DJANGO INSIDE FASTAPI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirlightLogistics.settings')
django.setup()

from core.models import Booking, Trip
from django.utils import timezone

app = FastAPI(title="Driver Boarding System")

class ScanRequest(BaseModel):
    booking_code: str

# Driver boarding page
@app.get("/", response_class=HTMLResponse)
async def driver_boarding_page():
    return """
    <html>
    <head><title>Driver Boarding - Student Safe Travel</title></head>
    <body style="font-family:Arial; text-align:center; margin-top:50px;">
        <h1>DRIVER BOARDING SYSTEM</h1>
        <p>Enter passenger booking code:</p>
        <input type="text" id="code" placeholder="e.g. A1B2C3D4" style="padding:15px; font-size:20px; width:300px;">
        <button onclick="scan()" style="padding:15px 30px; font-size:20px; margin:20px;">BOARD PASSENGER</button>
        <h2 id="result"></h2>
        <script>
        function scan() {
            const code = document.getElementById('code').value.trim().toUpperCase();
            if (!code) return;
            fetch('/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({booking_code: code})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('result').innerHTML = 
                        `<h2 style="color:green;">${data.message}<br>Seats: ${data.seats_taken}</h2>`;
                } else {
                    document.getElementById('result').innerHTML = 
                        `<h2 style="color:red;">${data.detail}</h2>`;
                }
            })
            .catch(() => {
                document.getElementById('result').innerHTML = '<h2 style="color:red;">Network error!</h2>';
            });
        }
        </script>
    </body>
    </html>
    """

# THE REAL SCAN ENDPOINT
@app.post("/scan")
async def scan_qr(request: ScanRequest):
    try:
        booking = Booking.objects.get(booking_code__iexact=request.booking_code)
        
        if booking.is_boarded:
            raise HTTPException(400, detail="Passenger already boarded!")
        
        if booking.trip.departure_date.date() != timezone.now().date():
            raise HTTPException(400, detail="Wrong trip date!")
        
        # BOARD PASSENGER
        booking.is_boarded = True
        booking.save()
        
        trip = booking.trip
        trip.passengers_boarded += 1
        trip.save()
        
        name = (booking.student.user.get_full_name() if booking.student 
                else booking.regular_passenger.full_name)
        user_type = "Student" if booking.student else "Regular Passenger"
        
        return {
            "success": True,
            "message": f"{name} ({user_type}) — BOARDED SUCCESSFULLY!",
            "seats_taken": f"{trip.passengers_boarded}/{trip.bus_capacity}"
        }
        
    except Booking.DoesNotExist:
        raise HTTPException(400, detail="Invalid booking code!")
    except Exception as e:
        raise HTTPException(400, detail="Error processing ticket")