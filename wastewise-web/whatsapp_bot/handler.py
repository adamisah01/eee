"""
WhatsApp Bot Webhook handler (Twilio).
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from fastapi import APIRouter, Request, Form
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()

@router.post('/webhook/')
async def twilio_whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Handle incoming WhatsApp messages from Twilio.
    """
    phone = From.replace('whatsapp:', '')
    text = Body.strip().lower()
    
    response = MessagingResponse()
    msg = response.message()
    
    if text in ['hi', 'hello', 'start']:
        msg.body(
            "Welcome to WasteWise! 🌱\n\n"
            "Reply with a number to book a pickup:\n"
            "1️⃣ General Household Waste\n"
            "2️⃣ Recyclables (Plastics/Cans)\n"
            "3️⃣ Bulk Waste (Furniture/Appliances)\n"
        )
    elif text == '1':
        msg.body(
            "Great! You selected General Household Waste.\n\n"
            "Please reply with your full pickup address."
        )
    else:
        # Simplistic conversational flow
        msg.body(
            "Thank you! Your order has been placed.\n"
            "A collector will be assigned shortly, and you will pay *only* after pickup.\n"
            "Track your order here: https://wastewise.ng/#/orders"
        )
        
    # Return TwiML XML
    from fastapi.responses import Response
    return Response(content=str(response), media_type="application/xml")
