"""
USSD Webhook handler (Africa's Talking).
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.post('/callback/', response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(default="")
):
    """
    Handle incoming USSD requests from Africa's Talking.
    """
    response = ""

    if text == "":
        response = "CON Welcome to WasteWise\n"
        response += "1. Book Pickup\n"
        response += "2. Track Order\n"
        response += "3. My Earnings (Collectors)"
    elif text == "1":
        response = "CON Select Waste Type\n"
        response += "1. General Waste\n"
        response += "2. Recyclables"
    elif text == "1*1" or text == "1*2":
        response = "CON Enter your house number and street name:"
    elif text.startswith("1*1*") or text.startswith("1*2*"):
        # End of flow
        response = "END Your pickup order is confirmed. A collector will call you soon. You pay after pickup."
    else:
        response = "END Invalid input. Please try again."

    return response
