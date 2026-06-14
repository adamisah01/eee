# WasteWise Web — Product Requirements Document (PRD)
**Version:** 1.0 — Web Stack Edition  
**Stack:** HTML5 · CSS3 · Vanilla JavaScript (ES6+) · Python (Django + FastAPI)  
**Last Updated:** 2026  
**Status:** Active Development

> **Note:** This is the web-stack version of WasteWise. Same product, same features, same backend — different frontend technology. The Python backend (Django + FastAPI + Celery + Django Channels) is **identical** to the React Native version. Only the UI layer changes: React Native → HTML/CSS/JS Progressive Web App (PWA).

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Target Users & Personas](#4-target-users--personas)
5. [Market Context & Competitors](#5-market-context--competitors)
6. [Core Value Proposition](#6-core-value-proposition)
7. [Web Stack Architecture](#7-web-stack-architecture)
8. [Frontend Technology Decisions](#8-frontend-technology-decisions)
9. [Feature Requirements](#9-feature-requirements)
   - [9.1 Customer Web App (PWA)](#91-customer-web-app-pwa)
   - [9.2 Collector Web App (PWA)](#92-collector-web-app-pwa)
   - [9.3 WhatsApp Bot](#93-whatsapp-bot)
   - [9.4 USSD Ordering (Offline)](#94-ussd-ordering-offline)
   - [9.5 Payment System (Pay-After)](#95-payment-system-pay-after)
   - [9.6 Real-Time GPS Tracking](#96-real-time-gps-tracking)
   - [9.7 Admin Dashboard](#97-admin-dashboard)
10. [Technical Architecture](#10-technical-architecture)
11. [Data Models](#11-data-models)
12. [API Contract](#12-api-contract)
13. [PWA Requirements](#13-pwa-requirements)
14. [Non-Functional Requirements](#14-non-functional-requirements)
15. [User Flows](#15-user-flows)
16. [Acceptance Criteria](#16-acceptance-criteria)
17. [Milestones & Roadmap](#17-milestones--roadmap)
18. [Out of Scope (v1)](#18-out-of-scope-v1)
19. [Risks & Mitigations](#19-risks--mitigations)
20. [Glossary](#20-glossary)

---

## 1. Executive Summary

WasteWise is an on-demand waste collection platform for Nigeria. This edition delivers the full product as a **Progressive Web App (PWA)** built with HTML5, CSS3, and Vanilla JavaScript — no frameworks, no build tools required. It runs in any browser on any device, installs to the home screen like a native app, and works partially offline.

The Python backend (Django + FastAPI + Celery + Django Channels) is unchanged from the React Native edition. The PWA replaces the React Native frontend with a pure web experience that is lighter, faster to deploy, easier to maintain, and accessible on devices that cannot install apps from the App Store or Google Play.

**Core differentiator:** Pay-after disposal model — users pay only after their waste is confirmed collected.

**PWA advantages for Nigeria:**
- Works on any Android or iOS browser — no app store approval needed
- Installable to home screen from Chrome/Safari ("Add to Home Screen")
- Offline order history via Service Worker cache
- Smaller footprint than native app — critical for low-storage devices
- Single codebase deployable as both website and "app"

---

## 2. Problem Statement

### For Waste Generators (Customers)
- No reliable on-demand waste pickup outside of estate subscriptions
- Paying upfront for informal services carries high risk of non-delivery
- Low-end Android devices (common in Nigeria) struggle with heavy native apps
- Many users prefer browser-based services to avoid storage/data cost of app downloads

### For Waste Collectors
- Work is informal with no guaranteed income or job queue
- No technology to find and reach customers efficiently
- Payments delayed or disputed with no accountability system
- Many collectors use low-end phones — a browser-based PWA is more accessible

### For the Environment
- Lagos generates ~15,000 metric tons of waste daily; 60%+ unmanaged
- Recyclables lost to landfills due to lack of collection infrastructure
- Illegal dumping causes flooding and disease outbreaks

---

## 3. Product Vision & Goals

### Vision
> "Make responsible waste disposal as easy as loading a webpage — available to every Nigerian on any device, any browser, any network."

### Goals

| Goal | Metric | Target (12 months) |
|------|--------|-------------------|
| User signups | Registered customers | 50,000 |
| Collector network | Active collectors | 2,000 |
| Order volume | Monthly pickups | 30,000 |
| Payment success | Pay-after conversion | ≥ 85% |
| PWA installs | "Add to Home Screen" | ≥ 40% of users |
| Coverage | Lagos LGAs covered | 15 of 20 |
| NPS | Net Promoter Score | ≥ 60 |
| USSD/WhatsApp orders | Non-app channel orders | ≥ 35% |

---

## 4. Target Users & Personas

### Persona 1 — Amaka, the Urban Renter
- **Age:** 29 | **Location:** Surulere, Lagos | **Device:** Android mid-range (Chrome)
- **Problem:** Rubbish piles up mid-week; no compound cleaner in her block
- **Need:** Quick booking from phone browser without downloading an app
- **Channel:** Web PWA (Chrome on Android)

### Persona 2 — Mallam Bello, the Market Trader
- **Age:** 52 | **Location:** Mushin, Lagos | **Device:** Basic Nokia feature phone
- **Problem:** Daily market waste; no data plan
- **Need:** Order pickup without internet
- **Channel:** USSD (`*384#`)

### Persona 3 — Chidi, the Keke Collector
- **Age:** 35 | **Location:** Isale-Eko | **Device:** Android low-end (2GB RAM)
- **Need:** Job queue, route map, weekly earnings payout
- **Channel:** Collector PWA (installed to home screen via Chrome)

### Persona 4 — Estate Manager
- **Role:** Facilities Manager | **Manages:** 120 residential units
- **Need:** Recurring scheduled pickups, billing reports
- **Channel:** Admin web dashboard (desktop browser)

---

## 5. Market Context & Competitors

| Platform | Geography | Gap vs WasteWise Web |
|----------|-----------|---------------------|
| Pakam | Lagos | Recyclables only; no pay-after; no PWA |
| Ecobarter | Abuja/Lagos | Requires upfront payment; app-only |
| Scrapays | Nigeria | AI recyclables only; no general waste |
| RecyclePoints | Nigeria | Rewards model only; no scheduling |
| Yo-Waste | Global | No USSD; English only; no pay-after |

### WasteWise Web Advantages
1. **No download required** — works in browser immediately
2. **Pay-after** — first in Nigeria to confirm before charging
3. **All waste types** — general, recyclable, organic, e-waste, bulky
4. **Triple channel** — Web + WhatsApp + USSD (all demographics)
5. **PWA installable** — feels native without App Store friction

---

## 6. Core Value Proposition

### For Customers
```
Open browser → Book in 60 seconds → Collector arrives → Waste removed → THEN you pay
```
- No app download — works from any browser link
- Pay-after: zero financial risk
- Works offline after first visit (Service Worker)

### For Collectors
```
Open browser → Go online → Receive job alert → Complete job → Get paid Friday
```
- No app store account needed
- GPS works from browser (Geolocation API)
- Camera for proof photos (MediaDevices API)

---

## 7. Web Stack Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (PWA)                            │
│                                                              │
│   HTML5 Templates  │  CSS3 (Custom Properties)  │  Vanilla JS│
│   ┌──────────────────────────────────────────────────────┐   │
│   │  Single Page App Router (hash-based, no framework)   │   │
│   │  Pages: home | order | track | payment | collector   │   │
│   └──────────────────────────────────────────────────────┘   │
│   Service Worker (offline cache) │ Web App Manifest (install) │
│   Google Maps JS API             │ WebSocket client           │
│   Paystack Inline JS             │ Fetch API (AJAX)           │
└──────────────────────────────────────────────────────────────┘
                          │ HTTPS / WSS
┌──────────────────────────────────────────────────────────────┐
│               PYTHON BACKEND (unchanged)                     │
│                                                              │
│   Django 4.2 (admin + auth + ORM)  │  FastAPI (REST API)    │
│   Django Channels (WebSocket)       │  Celery (background)   │
│   Supabase PostgreSQL + PostGIS     │  Redis                 │
└──────────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────────┐
│                EXTERNAL INTEGRATIONS                         │
│  Paystack │ Africa's Talking │ Twilio │ Google Maps          │
└──────────────────────────────────────────────────────────────┘
```

---

## 8. Frontend Technology Decisions

### Why Vanilla JS (no React/Vue/Angular)?

| Concern | Decision |
|---------|----------|
| No build step | Vanilla JS files served directly — no webpack/vite/babel |
| Bundle size | 0KB framework overhead — critical for Nigerian 3G/4G |
| Browser compatibility | ES6+ works on Chrome 60+, Safari 12+, covering 95%+ of Nigerian users |
| Maintainability | Fewer dependencies = fewer breaking changes |
| Hosting | Any static host (Nginx, Cloudflare Pages, Netlify) |
| PWA | Service Worker + Web App Manifest = native feel without a framework |

### CSS Approach
- CSS Custom Properties (variables) for theming
- CSS Grid + Flexbox for layout
- No CSS framework (Tailwind/Bootstrap) — custom design system
- Mobile-first responsive breakpoints
- CSS animations for transitions and loading states

### State Management
- No Redux/Zustand — plain JavaScript module pattern
- `window.AppState` object for global state
- `localStorage` for auth tokens and user session
- `sessionStorage` for temporary order data (wizard steps)

### Routing
- Hash-based SPA routing: `/#/home`, `/#/order`, `/#/track/ORDER_ID`
- No server-side routing needed — single `index.html` entry point
- Back button / history handled with `hashchange` event listener

### API Calls
- Native `fetch()` API throughout — no Axios dependency
- Central `api.js` module with auth header injection and token refresh
- All API calls async/await with centralized error handling

---

## 9. Feature Requirements

### 9.1 Customer Web App (PWA)

#### Authentication
- **REQ-U01:** Phone number login — enter number, receive OTP via SMS
- **REQ-U02:** 6-digit OTP verification page with auto-submit on 6th digit
- **REQ-U03:** JWT stored in `localStorage` with refresh token
- **REQ-U04:** Session persists across browser closes (remember me)
- **REQ-U05:** Auto-logout on token expiry with redirect to login

#### Home Dashboard (`/#/home`)
- **REQ-U06:** Active order status card with real-time status label
- **REQ-U07:** Quick-book grid: 5 waste type cards (icon, label, price)
- **REQ-U08:** Recent orders list (last 5, with status badge)
- **REQ-U09:** Pay-after trust banner always visible
- **REQ-U10:** Top navigation: logo, notifications bell, profile avatar

#### Order Creation (`/#/order/new`)
- **REQ-U11:** Multi-step form (3 steps) with progress indicator
- **REQ-U12:** Step 1: waste type selection (card grid, single select)
- **REQ-U13:** Step 2: address input + "Use my location" button (Geolocation API)
- **REQ-U14:** Step 2: time picker — "Now" toggle or datetime-local input
- **REQ-U15:** Step 2: special instructions textarea
- **REQ-U16:** Step 3: order summary card + price estimate + confirm button
- **REQ-U17:** Pay-after message displayed prominently at confirm step
- **REQ-U18:** Form state preserved in `sessionStorage` between steps (back button safe)
- **REQ-U19:** Loading spinner on submit; success redirect to tracking page

#### Order Tracking (`/#/track/{order_id}`)
- **REQ-U20:** Full-page Google Map with collector marker (animated pulse)
- **REQ-U21:** Collector marker updates via WebSocket (< 15s delay)
- **REQ-U22:** Bottom drawer (mobile) / right sidebar (desktop) showing:
  - Progress stepper (7 stages, green for completed)
  - Current status message
  - Collector name, rating, vehicle type, call button (tel: link)
  - Order amount
- **REQ-U23:** "Pay Now" button appears automatically when status = payment_pending
- **REQ-U24:** WebSocket reconnects automatically on disconnect
- **REQ-U25:** Offline indicator shown if connection lost

#### Payment (`/#/payment/{invoice_id}`)
- **REQ-U26:** Invoice breakdown: base + weight charge + platform fee = total
- **REQ-U27:** 24-hour countdown timer (live, updates every second)
- **REQ-U28:** "Pay Now" button → opens Paystack Inline popup (not redirect)
- **REQ-U29:** On Paystack success callback → verify with backend → show receipt
- **REQ-U30:** Receipt page: animated checkmark, order summary, download PDF link
- **REQ-U31:** Reminder banner at 6h and 18h (shown on next page load if unpaid)

#### Order History (`/#/orders`)
- **REQ-U32:** Filter tabs: All | Active | Paid | Cancelled
- **REQ-U33:** Paginated order list (20 per page)
- **REQ-U34:** Each order: status badge, order number, date, waste type, amount, "View" link
- **REQ-U35:** Order detail page: full timeline, photos, invoice, rating form

#### Profile (`/#/profile`)
- **REQ-U36:** Edit name, address, LGA
- **REQ-U37:** Order statistics: total orders, total spent
- **REQ-U38:** Notification preferences
- **REQ-U39:** Logout button

---

### 9.2 Collector Web App (PWA)

#### Collector-specific route: `/#/collector/*`
Detected from JWT payload (`role: "collector"`). Redirects customers away from collector routes.

- **REQ-C01:** Online/Offline toggle — prominent button on dashboard
- **REQ-C02:** Going online: `navigator.geolocation.getCurrentPosition()` → POST status
- **REQ-C03:** Earnings summary: today / this week / pending (fetched from API)
- **REQ-C04:** Active job card (if assigned job exists)
- **REQ-C05:** New job notification via WebSocket → browser Notification API alert
- **REQ-C06:** Accept/Decline job from notification or dashboard card
- **REQ-C07:** Active job page: step-by-step actions (En Route → Arrived → Collecting → Complete)
- **REQ-C08:** Photo capture on "Arrived" and "Complete" steps: `<input type="file" accept="image/*" capture="camera">`
- **REQ-C09:** Optional weight entry before marking complete
- **REQ-C10:** GPS stream every 10 seconds during active job via `setInterval` + Geolocation API
- **REQ-C11:** Map showing route to customer (Google Maps JS API Directions)
- **REQ-C12:** Job history page with earnings per job
- **REQ-C13:** Earnings page: wallet balance, payout history, bank account form
- **REQ-C14:** Profile page: ID upload, service areas, vehicle info

---

### 9.3 WhatsApp Bot
*(Identical to React Native version — backend only)*

- **REQ-W01–REQ-W13:** Same as PRD v1 (React Native). The WhatsApp bot is a pure backend service with no frontend dependency.

---

### 9.4 USSD Ordering (Offline)
*(Identical to React Native version — backend only)*

- **REQ-D01–REQ-D14:** Same as PRD v1 (React Native). The USSD handler is a pure backend service.

---

### 9.5 Payment System (Pay-After)
*(Backend identical — frontend implementation differs)*

- **REQ-P01–REQ-P16:** Same backend logic as v1
- **REQ-P-WEB-01:** Paystack payment uses **Inline JS** (`PaystackPop.setup()`) — no redirect needed
- **REQ-P-WEB-02:** Paystack inline popup opened by JavaScript on "Pay Now" click
- **REQ-P-WEB-03:** On Paystack `callback` event → fetch `/api/payments/verify/{reference}/` → show success UI
- **REQ-P-WEB-04:** Receipt rendered as HTML page, printable via `window.print()`

---

### 9.6 Real-Time GPS Tracking
*(Backend identical — frontend uses browser WebSocket API)*

- **REQ-G01–REQ-G11:** Same backend as v1
- **REQ-G-WEB-01:** Customer connects via `new WebSocket('wss://host/ws/order/{id}/track/')`
- **REQ-G-WEB-02:** GPS updates rendered on Google Maps JS API (`marker.setPosition()`)
- **REQ-G-WEB-03:** Collector uses `navigator.geolocation.watchPosition()` and sends via WebSocket
- **REQ-G-WEB-04:** WebSocket status shown as coloured dot in the UI (green = live, red = reconnecting)

---

### 9.7 Admin Dashboard
*(Same Django admin as v1 — accessed via browser at `/admin/`)*

All REQ-A01 through REQ-A11 are identical. The Django Admin is already a web-based interface, so no changes needed from the React Native version.

---

## 10. Technical Architecture

### File Structure

```
wastewise-web/
├── backend/                    # Python (identical to React Native version)
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── apps/
│   │   ├── users/
│   │   ├── orders/
│   │   ├── collectors/
│   │   ├── payments/
│   │   └── notifications/
│   ├── api/
│   │   └── main.py             # FastAPI
│   └── realtime/
│       └── consumers.py        # Django Channels
│
├── whatsapp_bot/
│   └── handler.py
│
├── ussd/
│   └── handler.py
│
└── frontend/                   # Pure HTML/CSS/JS PWA
    ├── index.html              # Single entry point
    ├── manifest.json           # PWA manifest
    ├── sw.js                   # Service Worker
    ├── offline.html            # Offline fallback page
    │
    ├── css/
    │   ├── variables.css       # CSS Custom Properties (design tokens)
    │   ├── reset.css           # CSS reset + base styles
    │   ├── components.css      # Buttons, cards, badges, forms
    │   ├── layout.css          # Grid, navigation, page containers
    │   ├── pages/
    │   │   ├── home.css
    │   │   ├── order.css
    │   │   ├── track.css
    │   │   ├── payment.css
    │   │   ├── collector.css
    │   │   └── auth.css
    │   └── animations.css      # Keyframes, transitions
    │
    ├── js/
    │   ├── app.js              # Entry point, router init
    │   ├── router.js           # Hash-based SPA router
    │   ├── api.js              # Fetch wrapper with auth
    │   ├── state.js            # Global AppState object
    │   ├── auth.js             # Login, OTP, JWT management
    │   ├── websocket.js        # WebSocket manager with reconnect
    │   ├── notifications.js    # Browser Notification API
    │   ├── geolocation.js      # GPS wrapper
    │   ├── storage.js          # localStorage/sessionStorage helpers
    │   └── pages/
    │       ├── home.js
    │       ├── newOrder.js
    │       ├── trackOrder.js
    │       ├── payment.js
    │       ├── orderHistory.js
    │       ├── orderDetail.js
    │       ├── profile.js
    │       ├── collector/
    │       │   ├── dashboard.js
    │       │   ├── activeJob.js
    │       │   ├── jobHistory.js
    │       │   ├── earnings.js
    │       │   └── collectorProfile.js
    │       └── auth/
    │           ├── login.js
    │           ├── otp.js
    │           └── register.js
    │
    ├── templates/              # HTML template strings (loaded by router)
    │   ├── home.html
    │   ├── newOrder.html
    │   ├── trackOrder.html
    │   ├── payment.html
    │   ├── orderHistory.html
    │   ├── orderDetail.html
    │   ├── profile.html
    │   ├── collector/
    │   │   ├── dashboard.html
    │   │   ├── activeJob.html
    │   │   ├── jobHistory.html
    │   │   └── earnings.html
    │   └── auth/
    │       ├── login.html
    │       ├── otp.html
    │       └── register.html
    │
    └── assets/
        ├── icons/              # PWA icons (192x192, 512x512)
        ├── images/             # Illustrations, logo
        └── sounds/             # Notification sound (optional)
```

### Backend Services (Port Map)

| Service | Port | Technology | Notes |
|---------|------|-----------|-------|
| Nginx (serves frontend + proxy) | 80/443 | Nginx Alpine | Serves static PWA files + proxies API |
| Django (ASGI/Admin/WebSocket) | 8000 | Daphne | WebSocket via /ws/ |
| FastAPI (REST API) | 8001 | Uvicorn | Mobile + web API |
| Redis | 6379 | Redis 7 | Celery broker + WS channel layer |

---

## 11. Data Models

*(Identical to React Native PRD — backend is shared)*

All models (User, OTPVerification, WasteCategory, PickupOrder, OrderStatusLog, CollectorProfile, CollectorLocationHistory, Invoice, Transaction, CollectorPayout) are exactly the same as specified in `WASTEWISE_PRD.md` v1.

---

## 12. API Contract

*(Identical to React Native PRD — same FastAPI endpoints)*

All endpoints are the same. The web frontend calls the same FastAPI (port 8001) and Django (port 8000) endpoints. The only difference is the Paystack integration:

**Web-specific: Paystack Inline**
- React Native version: Opens `invoice.payment_url` in a WebView
- Web version: Calls `PaystackPop.setup({...}).openIframe()` — opens inline popup in the same browser tab

```javascript
// Web Paystack Inline implementation
function openPaystackCheckout(invoice) {
  const handler = PaystackPop.setup({
    key: PAYSTACK_PUBLIC_KEY,
    email: currentUser.email || `${currentUser.phone}@wastewise.ng`,
    amount: invoice.total_amount_kobo,
    ref: invoice.paystack_reference,
    metadata: { order_number: invoice.order.order_number },
    callback: function(response) {
      // Payment successful — verify with backend
      verifyPayment(response.reference);
    },
    onClose: function() {
      showToast('Payment cancelled. You can pay anytime within 24 hours.');
    }
  });
  handler.openIframe();
}
```

---

## 13. PWA Requirements

### Web App Manifest (`manifest.json`)
- **PWA-01:** `name`: "WasteWise"
- **PWA-02:** `short_name`: "WasteWise"
- **PWA-03:** `start_url`: "/"
- **PWA-04:** `display`: "standalone" (hides browser chrome when installed)
- **PWA-05:** `theme_color`: "#16A34A" (green)
- **PWA-06:** `background_color`: "#F9FAFB"
- **PWA-07:** Icons at 72, 96, 128, 144, 152, 192, 384, 512px
- **PWA-08:** `orientation`: "portrait"
- **PWA-09:** `categories`: ["utilities", "lifestyle"]

### Service Worker (`sw.js`)
- **PWA-10:** Cache strategy: Cache-first for CSS/JS/HTML templates; Network-first for API calls
- **PWA-11:** Pre-cache on install: index.html, all CSS files, all JS files, offline.html
- **PWA-12:** Offline fallback: show `offline.html` for navigation requests when network fails
- **PWA-13:** Background sync: queue failed order submissions when offline, retry when online
- **PWA-14:** Push notification support: receive backend pushes via Web Push API
- **PWA-15:** Cache version management: increment cache name version on each deploy

### Install Prompt
- **PWA-16:** Intercept `beforeinstallprompt` event; show custom "Install App" banner
- **PWA-17:** Banner appears after user places second order (engagement threshold)
- **PWA-18:** Remember dismiss (localStorage) — don't show banner again if dismissed

### Offline Capabilities
- **PWA-19:** Order history readable offline (cached from last fetch)
- **PWA-20:** Active order status readable offline (cached)
- **PWA-21:** New order creation queued offline via Background Sync
- **PWA-22:** Offline indicator banner shown at top of page when offline

---

## 14. Non-Functional Requirements

### Performance
- **NFR-01:** First Contentful Paint (FCP) < 1.5s on 3G connection
- **NFR-02:** Time to Interactive (TTI) < 3s on 3G
- **NFR-03:** Total page weight (HTML + CSS + JS) < 150KB uncompressed
- **NFR-04:** All JS deferred/async — no render-blocking scripts
- **NFR-05:** Images lazy-loaded; WebP format preferred
- **NFR-06:** Lighthouse PWA score ≥ 90

### Compatibility
- **NFR-07:** Chrome 80+ on Android (primary target)
- **NFR-08:** Safari 14+ on iOS
- **NFR-09:** Firefox 80+ on desktop
- **NFR-10:** Minimum screen width: 320px (small Android phones)
- **NFR-11:** Touch targets minimum 44×44px
- **NFR-12:** No JavaScript framework dependency — no CDN single point of failure

### Security
- **NFR-13:** JWT stored in `localStorage` (not cookies, to avoid CSRF)
- **NFR-14:** All API calls over HTTPS
- **NFR-15:** Content Security Policy (CSP) header configured
- **NFR-16:** No inline JavaScript (CSP compliant)
- **NFR-17:** Paystack public key only (never secret key) in frontend code
- **NFR-18:** OTP expires in 5 minutes, single use

### Reliability
- **NFR-19:** Service Worker ensures app loads offline after first visit
- **NFR-20:** WebSocket reconnects within 3 seconds
- **NFR-21:** All API calls have 10s timeout with user-facing error messages
- **NFR-22:** Failed actions show toast notification with retry option

### Accessibility
- **NFR-23:** WCAG 2.1 AA compliance
- **NFR-24:** All interactive elements keyboard-navigable
- **NFR-25:** ARIA labels on all icon-only buttons
- **NFR-26:** Colour contrast ratio ≥ 4.5:1 for all text
- **NFR-27:** Screen reader compatible (VoiceOver/TalkBack)

---

## 15. User Flows

### Flow 1 — Customer Books via Web Browser (Happy Path)

```
User visits wastewise.ng in Chrome on Android
  → App loads (< 2s on 3G)
  → If first visit: "Add to Home Screen" banner appears after scroll
  → Login page: enter +2348031234567
  → Tap "Get OTP" → SMS arrives in 15 seconds
  → 6-digit OTP input → auto-submits on digit 6 → logged in
  → Home page: "Good morning, Amaka 👋"
  → Tap "General Household" card in Quick Book grid
  → Step 1: waste type pre-filled → "Continue"
  → Step 2: address input → tap "Use my location" → browser asks permission → granted
           → address auto-filled: "12 Balogun St, Surulere, Lagos"
           → select "Right Now" schedule → "Continue"
  → Step 3: Summary — Waste: General Household | ₦500+ | Now
           → "💡 You pay ONLY after waste is collected" (green banner)
           → Tap "Confirm Pickup 🎉"
           → Loading spinner → order created
  → Redirect to /#/track/WW12345678
  → Full-screen map with "Searching for collector..." status
  → 45 seconds: status updates to "Collector Assigned" — Emeka on map
  → Browser notification: "Collector assigned — Emeka is on the way!"
  → Emeka's green dot moves on map toward home icon
  → Status updates: En Route → Arrived
  → 20 minutes later: status → "payment_pending"
  → "Pay Now" button appears at bottom of tracking page
  → Tap "Pay Now" → Paystack inline popup opens
  → Enter card / use saved card / bank transfer
  → Payment success → popup closes → receipt page shows
  → Green checkmark animation + "Payment Successful! ₦550"
  → "⭐ Rate Emeka" prompt → 5 stars → done
```

### Flow 2 — Collector Accepts and Completes Job

```
Collector opens wastewise.ng/collector in Chrome
  → Logs in with phone + OTP
  → Collector Dashboard: "⚫ You are Offline"
  → Tap "Go Online" toggle
  → Browser asks location permission → granted → location sent to API
  → Status: "🟢 You are Online" — green background
  → WebSocket connected: green "Live" dot
  → 3 minutes later: notification toast + browser notification:
    "🚨 New Job! General waste — 12 Balogun St, Surulere — ₦765 — 2.1km"
  → Accept/Decline buttons → tap Accept
  → Active Job page opens with Google Map showing route
  → "Start Journey" button → tap → sends "en_route" to WebSocket
  → Arrive at location → "I've Arrived" button → tap
  → Photo prompt: "Take a photo of the waste"
    → tap camera icon → native camera opens (capture="camera")
    → take photo → photo preview shown → "Continue"
  → "Start Collecting" button → loading waste
  → Optional: enter "8.5" in weight field
  → "Mark Complete ✅" → confirmation dialog → confirm
    → disposal photo prompt → take photo → submit
  → "✅ Job Done! Customer notified to pay."
  → Dashboard shows: "₦765 added to pending earnings"
```

---

## 16. Acceptance Criteria

*(Same as React Native PRD v1, with these web-specific additions)*

### PWA
- [ ] App installs to Android home screen via Chrome "Add to Home Screen"
- [ ] App installs to iOS home screen via Safari "Share → Add to Home Screen"
- [ ] App loads from home screen icon without address bar (standalone mode)
- [ ] App loads offline after first visit (Service Worker cache)
- [ ] Order history visible offline

### Web Payment
- [ ] Paystack Inline popup opens on "Pay Now" click (no page redirect)
- [ ] Payment completion closes popup and shows receipt on same page
- [ ] Receipt prints correctly with `window.print()`

### Browser APIs
- [ ] Geolocation API works on Chrome Android (HTTPS required)
- [ ] Camera input works on mobile (`<input capture="camera">`)
- [ ] Browser Notification API shows job alerts when permission granted
- [ ] WebSocket connects and shows real-time GPS updates on map

### Responsiveness
- [ ] Layout correct at 320px (small phone), 375px (iPhone SE), 768px (tablet), 1280px (desktop)
- [ ] Touch targets ≥ 44px on mobile
- [ ] No horizontal scrolling on any screen width

---

## 17. Milestones & Roadmap

### Phase 1 — Web MVP (Months 1–3)
- [ ] Backend (identical to React Native version)
- [ ] HTML/CSS design system (variables, components, layout)
- [ ] SPA router + auth flow
- [ ] Customer web app: Home, NewOrder, TrackOrder, Payment, History
- [ ] Collector web app: Dashboard, ActiveJob, Earnings
- [ ] Service Worker (offline cache)
- [ ] PWA manifest + install prompt
- [ ] WhatsApp bot + USSD (backend)
- [ ] Docker + Nginx serving static files
- [ ] Beta: 3 Lagos LGAs

### Phase 2 — Enhancement (Months 4–6)
- [ ] Web Push Notifications (full Web Push API implementation)
- [ ] Background Sync for offline order queuing
- [ ] Estate recurring scheduling module
- [ ] Yoruba language toggle
- [ ] Collector earnings chart (Canvas API or Chart.js CDN)
- [ ] Admin analytics charts

### Phase 3 — Scale (Months 7–12)
- [ ] Abuja market launch
- [ ] Port Harcourt launch
- [ ] SEO optimization (server-side rendering for landing page)
- [ ] Performance budget enforcement (Lighthouse CI)
- [ ] Series A fundraising documentation

---

## 18. Out of Scope (v1)

- Hazardous waste collection
- In-app text chat between customer and collector
- Waste sorting facility partnerships
- International markets
- Desktop-optimized admin (uses Django Admin)
- Server-side rendering (SSR) for PWA pages

---

## 19. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Safari iOS PWA limitations | High | Medium | Test all features on Safari; document iOS-specific fallbacks |
| Geolocation blocked by user | High | Medium | Manual address entry always available; geolocation optional |
| Camera capture fails on some Android | Medium | Low | File upload fallback (`<input type="file">` without capture) |
| 3G slow loads for large JS | Medium | High | Strict 150KB budget; code split per page; lazy load non-critical |
| localStorage cleared by browser | Low | Medium | Re-authenticate flow handles gracefully; detect and redirect |
| Paystack popup blocked | Low | Medium | Detect popup block; fall back to redirect to payment_url |

---

## 20. Glossary

| Term | Definition |
|------|-----------|
| PWA | Progressive Web App — web app installable to home screen with offline support |
| Service Worker | JavaScript file running in background, handles caching and offline behaviour |
| Web App Manifest | JSON file describing the PWA (name, icon, colours, display mode) |
| Hash Router | SPA routing using URL hash (`/#/page`) — no server config needed |
| Inline JS | Paystack payment method that opens a popup in the current page |
| CSS Custom Properties | CSS variables defined with `--name: value` syntax |
| Geolocation API | Browser API for getting user's GPS coordinates |
| MediaDevices API | Browser API for accessing camera and microphone |
| Notification API | Browser API for showing system notifications |
| Background Sync | Service Worker feature to retry failed requests when connectivity returns |
| Fetch API | Modern browser API replacing XMLHttpRequest for HTTP calls |
| Kobo | Smallest Nigerian currency unit (100 kobo = ₦1). All money stored as integer kobo |
| Pay-After Gate | System trigger when collector marks complete → invoice created → payment requested |
| PostGIS | PostgreSQL extension for geographic queries (nearest collector, geofence) |
| LGA | Local Government Area — subdivision of Lagos State used for zone routing |

---

*WasteWise Web PRD v1.0 — HTML/CSS/JS + Python Edition. Maintained by WasteWise Product Team.*
