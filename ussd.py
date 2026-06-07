"""
ussd/handler.py
Africa's Talking USSD handler for WasteWise.
Mounts at /ussd/session/ in Django urls.py

When user dials *384*XXXX# → Africa's Talking POSTs to this endpoint.
We return a CON (continue) or END (end session) string.

Session stored in Redis with sessionId as key.
No internet required on the user's phone — just basic GSM.

Menu tree:
  Main → 1. Book Pickup → Waste type → Address → Time → Confirm
       → 2. Order Status
       → 3. Pay Invoice (get payment code for USSD banking)
       → 4. Help
"""
import json
import redis
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)
SESSION_TTL = 60 * 20  # 20 min USSD session


def _get(session_id: str) -> dict:
    data = r.get(f"ussd:{session_id}")
    return json.loads(data) if data else {}


def _save(session_id: str, data: dict):
    r.set(f"ussd:{session_id}", json.dumps(data), ex=SESSION_TTL)


def _clear(session_id: str):
    r.delete(f"ussd:{session_id}")


@csrf_exempt
def ussd_callback(request):
    """Africa's Talking USSD callback endpoint."""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    session_id = request.POST.get("sessionId", "")
    phone = request.POST.get("phoneNumber", "").replace("+", "")
    network = request.POST.get("networkCode", "")
    text = request.POST.get("text", "")  # All inputs joined by *

    response = handle_session(session_id, phone, text, network)
    return HttpResponse(response, content_type="text/plain")


def handle_session(session_id: str, phone: str, text: str, network: str) -> str:
    """
    Route USSD session based on accumulated input text.
    Africa's Talking sends cumulative input: "1*2*Lagos" etc.
    """
    parts = [p.strip() for p in text.split("*") if p.strip()] if text else []
    depth = len(parts)

    session = _get(session_id)

    # Root menu
    if depth == 0:
        _save(session_id, {"phone": phone, "network": network})
        return con(
            "CON Welcome to WasteWise\n"
            "On-demand waste pickup\n"
            "Pay AFTER collection!\n\n"
            "1. Book Pickup\n"
            "2. Check Order Status\n"
            "3. Pay Invoice\n"
            "4. Help"
        )

    choice_1 = parts[0]

    # ── BOOK PICKUP ───────────────────────────────────────────────────────────
    if choice_1 == "1":
        if depth == 1:
            return con(
                "CON Select waste type:\n\n"
                "1. General household (N500)\n"
                "2. Recyclables (N300)\n"
                "3. Organic/food waste (N400)\n"
                "4. Electronics/e-waste (N800)\n"
                "5. Bulky items (N1500)"
            )

        waste_map = {
            "1": ("General Household", 500, "general"),
            "2": ("Recyclables", 300, "recyclable"),
            "3": ("Organic/Food", 400, "organic"),
            "4": ("Electronics", 800, "electronic"),
            "5": ("Bulky Items", 1500, "bulky"),
        }
        choice_waste = parts[1]

        if choice_waste not in waste_map:
            return end("END Invalid option. Please dial again.")

        waste_name, waste_price, waste_type = waste_map[choice_waste]
        session["waste"] = {"name": waste_name, "price": waste_price, "type": waste_type}
        _save(session_id, session)

        if depth == 2:
            return con(
                "CON Enter pickup address:\n"
                "(We use your network location + address)\n\n"
                "1. Use my registered address\n"
                "2. Enter new address"
            )

        choice_addr = parts[2]

        if choice_addr == "1":
            # Use saved address from user profile
            address = get_user_address(phone)
            session["address"] = address or "Registered address"
            session["use_saved_address"] = True
            _save(session_id, session)

            if depth == 3:
                return con(
                    f"CON Address: {session['address'][:30]}...\n\n"
                    "When should we pick up?\n"
                    "1. Right now (30-60 mins)\n"
                    "2. In 2 hours\n"
                    "3. Tomorrow morning (8am)"
                )

        elif choice_addr == "2":
            if depth == 3:
                return con(
                    "CON Type your area/landmark:\n"
                    "(e.g. Surulere, near Total filling)\n\n"
                    "Enter below:"
                )
            # depth == 4: user typed their address
            session["address"] = parts[3]
            _save(session_id, session)

            if depth == 4:
                return con(
                    f"CON Address noted: {parts[3][:25]}...\n\n"
                    "When should we pick up?\n"
                    "1. Right now (30-60 mins)\n"
                    "2. In 2 hours\n"
                    "3. Tomorrow morning (8am)"
                )

        # Time selection (varies by address depth offset)
        time_depth = 4 if session.get("use_saved_address") else 5
        if depth == time_depth:
            time_input = parts[-1]
            time_map = {
                "1": "Right now (30–60 mins)",
                "2": "In 2 hours",
                "3": "Tomorrow 8am",
            }
            if time_input not in time_map:
                return end("END Invalid time option. Please dial again.")

            session["time"] = time_map[time_input]
            _save(session_id, session)

            waste = session.get("waste", {})
            address = session.get("address", "Your address")
            price = waste.get("price", 0)

            return con(
                f"CON CONFIRM ORDER:\n"
                f"Waste: {waste.get('name')}\n"
                f"Address: {address[:20]}...\n"
                f"Time: {session['time']}\n"
                f"Est. price: N{price:,}\n"
                f"Pay AFTER pickup!\n\n"
                f"1. Confirm\n"
                f"2. Cancel"
            )

        # Confirmation
        if depth == time_depth + 1:
            final_choice = parts[-1]
            if final_choice == "1":
                result = place_ussd_order(phone, session)
                if result:
                    _clear(session_id)
                    return end(
                        f"END Order placed!\n"
                        f"Order #: {result.get('order_number')}\n"
                        f"We'll send SMS when collector is assigned.\n"
                        f"You pay ONLY after pickup!\n"
                        f"Thank you - WasteWise"
                    )
                else:
                    return end("END Error placing order. Please try again or call 0800-WASTEWISE.")
            else:
                _clear(session_id)
                return end("END Order cancelled. Dial *384*XXXX# to start again.")

    # ── ORDER STATUS ──────────────────────────────────────────────────────────
    elif choice_1 == "2":
        order = get_latest_order(phone)
        if not order:
            return end("END No recent orders found.\nDial again to book a pickup.")

        status_map = {
            "pending": "Searching for collector...",
            "assigned": "Collector assigned!",
            "en_route": "Collector on the way",
            "arrived": "Collector at your location",
            "collecting": "Collecting your waste",
            "payment_pending": "Please pay! (see SMS)",
            "paid": "Complete! Thank you",
            "cancelled": "Order was cancelled",
        }
        status_text = status_map.get(order.get("status", ""), "Unknown")
        return end(
            f"END Order #{order.get('order_number')}\n"
            f"Status: {status_text}\n"
            f"Amount: N{order.get('total_naira', 0):,.0f}\n\n"
            f"WasteWise"
        )

    # ── PAY INVOICE ───────────────────────────────────────────────────────────
    elif choice_1 == "3":
        invoice = get_unpaid_invoice(phone)
        if not invoice:
            return end("END No outstanding payments.\nDial again to book a pickup.")

        if depth == 1:
            return con(
                f"CON Invoice #{invoice.get('invoice_number')}\n"
                f"Amount: N{invoice.get('total_naira', 0):,.0f}\n"
                f"Due: {invoice.get('due_at', 'Soon')[:10]}\n\n"
                f"Pay via:\n"
                f"1. USSD (bank transfer)\n"
                f"2. Get SMS payment link"
            )

        pay_choice = parts[1]
        if pay_choice == "2":
            send_payment_sms(phone, invoice)
            return end(
                f"END Payment link sent via SMS!\n"
                f"Amount: N{invoice.get('total_naira', 0):,.0f}\n"
                f"Check your messages now."
            )
        elif pay_choice == "1":
            return end(
                f"END Transfer N{invoice.get('total_naira', 0):,.0f} to:\n"
                f"Bank: WasteWise (GTBank)\n"
                f"Account: 0123456789\n"
                f"Ref: {invoice.get('invoice_number')}\n\n"
                f"We'll confirm via SMS."
            )

    # ── HELP ──────────────────────────────────────────────────────────────────
    elif choice_1 == "4":
        return end(
            "END WasteWise Help\n"
            "Call: 0800-WASTEWISE\n"
            "SMS: 0700-WASTE-NG\n"
            "WhatsApp: 0812-WASTEWISE\n\n"
            "We collect your waste.\n"
            "You pay AFTER pickup!"
        )

    else:
        return end("END Invalid option. Please dial *384*XXXX# to try again.")


def con(text: str) -> str:
    """Continue session."""
    return text if text.startswith("CON") else f"CON {text}"


def end(text: str) -> str:
    """End session."""
    return text if text.startswith("END") else f"END {text}"


# ─── Internal API calls to Django ─────────────────────────────────────────────

def place_ussd_order(phone: str, session: dict) -> dict:
    import requests
    try:
        resp = requests.post(
            "http://localhost:8000/internal/orders/create-ussd/",
            json={
                "phone_number": f"+{phone}",
                "waste_type": session["waste"]["type"],
                "pickup_address": session.get("address"),
                "scheduled_time": None,
                "channel": "ussd",
            },
            timeout=10,
        )
        if resp.status_code == 201:
            return resp.json()
        return None
    except Exception:
        return None


def get_latest_order(phone: str) -> dict:
    import requests
    try:
        resp = requests.get(
            "http://localhost:8000/internal/orders/latest/",
            params={"phone": f"+{phone}"},
            timeout=5,
        )
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None


def get_user_address(phone: str) -> str:
    import requests
    try:
        resp = requests.get(
            "http://localhost:8000/internal/users/address/",
            params={"phone": f"+{phone}"},
            timeout=5,
        )
        return resp.json().get("address") if resp.status_code == 200 else None
    except Exception:
        return None


def get_unpaid_invoice(phone: str) -> dict:
    import requests
    try:
        resp = requests.get(
            "http://localhost:8000/internal/invoices/unpaid/",
            params={"phone": f"+{phone}"},
            timeout=5,
        )
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None


def send_payment_sms(phone: str, invoice: dict):
    import requests
    try:
        requests.post(
            "http://localhost:8000/internal/notifications/sms/",
            json={
                "phone": f"+{phone}",
                "message": (
                    f"WasteWise Payment\n"
                    f"Invoice: {invoice.get('invoice_number')}\n"
                    f"Amount: N{invoice.get('total_naira', 0):,.0f}\n"
                    f"Pay: {invoice.get('payment_url')}"
                ),
            },
            timeout=5,
        )
    except Exception:
        pass