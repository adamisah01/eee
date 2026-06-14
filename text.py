"""
whatsapp_bot/handler.py
Menu-driven WhatsApp ordering bot for WasteWise.
Mounts at /whatsapp/webhook/ in Django urls.py

Conversation states (stored in Redis by phone number):
  - idle          → greeting, show main menu
  - select_waste  → choose waste category
  - enter_address → type pickup address
  - confirm_time  → now / schedule
  - confirming    → show summary, confirm Y/N
  - awaiting_payment → order placed, payment pending
"""
import json
import redis
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.twiml.messaging_response import MessagingResponse

logger = logging.getLogger(__name__)
r = redis.from_url(settings.REDIS_URL)

SESSION_TTL = 60 * 30  # 30 minute session


# ─── Session helpers ──────────────────────────────────────────────────────────

def get_session(phone: str) -> dict:
    data = r.get(f"wa:session:{phone}")
    return json.loads(data) if data else {"state": "idle", "data": {}}


def save_session(phone: str, session: dict):
    r.set(f"wa:session:{phone}", json.dumps(session), ex=SESSION_TTL)


def clear_session(phone: str):
    r.delete(f"wa:session:{phone}")


# ─── Menu strings ─────────────────────────────────────────────────────────────

MAIN_MENU = """👋 Welcome to *WasteWise*!
Nigeria's on-demand waste pickup 🗑️

Reply with a number:
*1* — Book a pickup
*2* — Check my order status
*3* — View my invoices / Pay
*4* — Help & Support
*0* — Exit"""

WASTE_MENU = """What type of waste?

*1* — 🗑️ General household (₦500)
*2* — ♻️ Recyclables — plastic, paper (₦300)
*3* — 🍂 Organic / food waste (₦400)
*4* — 💻 Electronics / e-waste (₦800)
*5* — 🛋️ Bulky items / furniture (₦1,500)
*0* — Back to main menu"""

TIME_MENU = """When should we pick up?

*1* — 🚀 Right now (within 30–60 mins)
*2* — 📅 Schedule for later (tell me the time)
*0* — Back"""

CONFIRM_TEMPLATE = """📋 *Order Summary*

🗑️ Waste type: {waste_type}
📍 Address: {address}
⏰ Time: {time}
💰 Estimated: ₦{price}

✅ Reply *YES* to confirm
❌ Reply *NO* to cancel"""


WASTE_OPTIONS = {
    "1": {"name": "General Household Waste", "price": 500, "type": "general"},
    "2": {"name": "Recyclables", "price": 300, "type": "recyclable"},
    "3": {"name": "Organic / Food Waste", "price": 400, "type": "organic"},
    "4": {"name": "Electronics / E-waste", "price": 800, "type": "electronic"},
    "5": {"name": "Bulky Items / Furniture", "price": 1500, "type": "bulky"},
}


# ─── Main webhook handler ─────────────────────────────────────────────────────

@csrf_exempt
def whatsapp_webhook(request):
    """Twilio webhook — receives incoming WhatsApp messages."""
    if request.method != "POST":
        return HttpResponse(status=405)

    phone = request.POST.get("From", "").replace("whatsapp:", "").replace("+", "")
    message = request.POST.get("Body", "").strip()
    profile_name = request.POST.get("ProfileName", "there")

    session = get_session(phone)
    response_text = route_message(phone, message, session, profile_name)

    twiml = MessagingResponse()
    twiml.message(response_text)
    return HttpResponse(str(twiml), content_type="application/xml")


def route_message(phone: str, message: str, session: dict, name: str) -> str:
    """Route message to correct handler based on conversation state."""
    msg = message.strip().upper()
    state = session.get("state", "idle")

    # Global commands work from any state
    if msg in ("0", "EXIT", "CANCEL", "QUIT"):
        clear_session(phone)
        return "👋 Session ended. Type *HI* anytime to start a new pickup."

    if msg in ("HELP", "SUPPORT"):
        return "📞 Support: Call 0800-WASTEWISE or email support@wastewise.ng\nReply with any number to continue."

    if msg in ("STATUS", "ORDER STATUS"):
        return handle_status_check(phone)

    # State machine
    handlers = {
        "idle": handle_idle,
        "select_waste": handle_waste_selection,
        "enter_address": handle_address_entry,
        "confirm_time": handle_time_selection,
        "enter_custom_time": handle_custom_time,
        "confirming": handle_confirmation,
    }

    handler = handlers.get(state, handle_idle)
    return handler(phone, message, session, name)


def handle_idle(phone, message, session, name):
    msg = message.strip().upper()
    if msg in ("1", "BOOK", "ORDER", "PICKUP"):
        save_session(phone, {"state": "select_waste", "data": {}})
        return WASTE_MENU
    elif msg in ("2",):
        return handle_status_check(phone)
    elif msg in ("3", "PAY", "INVOICE"):
        return handle_invoice_check(phone)
    else:
        return f"Hi *{name}*! 👋\n\n" + MAIN_MENU


def handle_waste_selection(phone, message, session, name):
    choice = message.strip()
    if choice not in WASTE_OPTIONS:
        return f"Please reply 1–5 to select waste type, or 0 to go back.\n\n{WASTE_MENU}"

    waste = WASTE_OPTIONS[choice]
    session["data"]["waste"] = waste
    session["state"] = "enter_address"
    save_session(phone, session)

    return (
        f"✅ Selected: *{waste['name']}*\n\n"
        f"📍 Please type your *full pickup address*\n"
        f"(e.g., 12 Balogun Street, Surulere, Lagos)\n\n"
        f"Or reply *0* to go back."
    )


def handle_address_entry(phone, message, session, name):
    if len(message.strip()) < 10:
        return "Please type your full pickup address (at least 10 characters)."

    session["data"]["address"] = message.strip()
    session["state"] = "confirm_time"
    save_session(phone, session)
    return TIME_MENU


def handle_time_selection(phone, message, session, name):
    choice = message.strip()
    if choice == "1":
        session["data"]["time"] = "Now (30–60 mins)"
        session["data"]["scheduled"] = None
        session["state"] = "confirming"
        save_session(phone, session)
        return build_confirmation(session)
    elif choice == "2":
        session["state"] = "enter_custom_time"
        save_session(phone, session)
        return (
            "📅 Please type your preferred pickup time:\n"
            "(e.g., *Tomorrow 9am* or *Friday 3pm*)\n\n"
            "Reply *0* to go back."
        )
    else:
        return f"Please reply *1* or *2*.\n\n{TIME_MENU}"


def handle_custom_time(phone, message, session, name):
    session["data"]["time"] = message.strip()
    session["data"]["scheduled"] = message.strip()
    session["state"] = "confirming"
    save_session(phone, session)
    return build_confirmation(session)


def handle_confirmation(phone, message, session, name):
    msg = message.strip().upper()

    if msg in ("YES", "Y", "CONFIRM", "OK"):
        return place_order_from_whatsapp(phone, session, name)
    elif msg in ("NO", "N", "CANCEL"):
        clear_session(phone)
        return "❌ Order cancelled. Type *HI* to start a new one."
    else:
        return f"Please reply *YES* to confirm or *NO* to cancel.\n\n{build_confirmation(session)}"


def build_confirmation(session):
    d = session["data"]
    waste = d.get("waste", {})
    return CONFIRM_TEMPLATE.format(
        waste_type=waste.get("name", "Unknown"),
        address=d.get("address", "Not set"),
        time=d.get("time", "Now"),
        price=f"{waste.get('price', 0):,}",
    )


def place_order_from_whatsapp(phone, session, name):
    """Create order in Django backend and confirm to user."""
    import requests as req
    from django.conf import settings

    d = session["data"]
    waste = d.get("waste", {})

    try:
        resp = req.post(
            "http://localhost:8000/internal/orders/create-whatsapp/",
            json={
                "phone_number": f"+{phone}",
                "waste_type": waste.get("type"),
                "pickup_address": d.get("address"),
                "scheduled_time": d.get("scheduled"),
                "channel": "whatsapp",
            },
            timeout=15,
        )
        data = resp.json()
        order_number = data.get("order_number", "N/A")

        clear_session(phone)

        return (
            f"🎉 *Order confirmed, {name.split()[0]}!*\n\n"
            f"📦 Order #: *{order_number}*\n"
            f"🗑️ Waste: {waste.get('name')}\n"
            f"📍 Pickup: {d.get('address')}\n"
            f"⏰ Time: {d.get('time')}\n\n"
            f"We'll notify you when a collector is on their way! 🚴\n\n"
            f"💡 *Pay only after your waste is collected.*\n\n"
            f"Reply *STATUS* anytime to check your order."
        )
    except Exception as e:
        logger.error(f"WhatsApp order creation failed: {e}")
        return (
            "Sorry, there was an error placing your order. 😔\n"
            "Please try again or call 0800-WASTEWISE for help."
        )


def handle_status_check(phone):
    """Check latest order status for this phone number."""
    import requests as req
    try:
        resp = req.get(
            "http://localhost:8000/internal/orders/latest/",
            params={"phone": f"+{phone}"},
            timeout=10,
        )
        if resp.status_code == 404:
            return "You have no recent orders. Reply *1* to book a pickup."
        data = resp.json()
        status_emoji = {
            "pending": "⏳",
            "assigned": "🚴",
            "en_route": "🚴 On the way!",
            "arrived": "📍 Arrived!",
            "collecting": "🗑️ Collecting...",
            "payment_pending": "💳 Please pay!",
            "paid": "✅ Complete!",
            "cancelled": "❌ Cancelled",
        }
        status = data.get("status", "unknown")
        emoji = status_emoji.get(status, "ℹ️")
        return (
            f"📦 Order *{data.get('order_number')}*\n"
            f"Status: {emoji} {status.replace('_', ' ').title()}\n"
            f"Waste: {data.get('waste_category')}\n"
            f"Amount: ₦{data.get('total_naira', 0):,.2f}\n\n"
            f"Reply *MENU* to go back."
        )
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return "Could not retrieve order status. Please try again."


def handle_invoice_check(phone):
    """Return unpaid invoice link for the user."""
    import requests as req
    try:
        resp = req.get(
            "http://localhost:8000/internal/invoices/unpaid/",
            params={"phone": f"+{phone}"},
            timeout=10,
        )
        if resp.status_code == 404:
            return "✅ No outstanding payments! Type *1* to book a pickup."
        data = resp.json()
        return (
            f"💳 *Unpaid Invoice*\n\n"
            f"Order: {data.get('order_number')}\n"
            f"Amount: ₦{data.get('total_naira', 0):,.2f}\n"
            f"Due: {data.get('due_at')}\n\n"
            f"🔗 Pay here:\n{data.get('payment_url')}"
        )
    except Exception:
        return "Could not retrieve invoice. Please try again or call support."
