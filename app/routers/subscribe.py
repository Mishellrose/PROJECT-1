from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import razorpay
import json

from app import oauth2
from app.database import get_db
from ..config import settings  # loads from .env

router = APIRouter(prefix="/subscribe", tags=["Subscription"])

# Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# 💰 Plan amounts (in paise)
PLAN_ONE_MONTH_AMOUNT = 100   # ₹100
PLAN_THREE_MONTH_AMOUNT = 300  # ₹250


# 1️⃣ CREATE PAYMENT LINK
@router.post("/create-payment-link")
def create_payment_link(plan: str, current_user=Depends(oauth2.get_current_user)):
    """
    Create a Razorpay payment link for either 1-month or 3-month subscription
    """
    if plan not in ["1_month", "3_months"]:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

    # Pick amount based on plan
    amount = PLAN_ONE_MONTH_AMOUNT if plan == "1_month" else PLAN_THREE_MONTH_AMOUNT

    try:
        payment_link = client.payment_link.create({
            "amount": amount,
            "currency": "INR",
            "accept_partial": False,
            "description": f"{plan.replace('_', ' ').title()} Subscription",
            "customer": {
                "name": current_user.name,
                "email": current_user.email
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            # ✅ Redirect user to callback after payment
            "callback_url": f"{settings.WEBHOOK_URL}/subscribe/callback",
            "notes": {
                "user_id": current_user.id,
                "plan": plan
            }
        })

        return {
            "message": "Payment link created successfully",
            "plan": plan,
            "payment_link": payment_link["short_url"],
            "status": payment_link["status"],
            "id": payment_link["id"]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create payment link: {str(e)}")


# 2️⃣ CALLBACK (User browser redirect)
@router.get("/callback")
async def payment_callback(request: Request):
    """
    Razorpay redirects the user here after payment.
    """
    params = dict(request.query_params)
    print("💬 Callback received:", params)

    if params.get("razorpay_payment_link_status") == "paid":
        return {"message": "✅ Payment successful! Your subscription will activate shortly."}
    else:
        return {"message": "❌ Payment not completed or failed."}


# 3️⃣ WEBHOOK (Server-to-Server confirmation)
@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Razorpay sends a webhook here when a payment_link is paid.
    """
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty webhook body")

    signature = request.headers.get("x-razorpay-signature")
    print("Signature:", signature)

    try:
        body_str = body.decode("utf-8")
        client.utility.verify_webhook_signature(
            body_str, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = json.loads(body_str)
    event = payload.get("event")
    print("📩 Received event:", event)

    if event == "payment_link.paid":
        notes = payload["payload"]["payment_link"]["entity"]["notes"]
        print("🧾 Notes:", notes)

        user_id = notes.get("user_id")
        plan = notes.get("plan") or "1_month"

        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id in notes")

        validity_days = 30 if plan == "1_month" else 90
        expiry_date = datetime.utcnow() + timedelta(days=validity_days)

        # ✅ Update user to premium
        db.execute(text("""
            UPDATE "user" SET "isPremium" = TRUE, "subscription_expiry" = :expiry
            WHERE id = :uid
        """), {"uid": user_id, "expiry": expiry_date})
        db.commit()

        # ✅ Record in subscription table
        db.execute(text("""
            INSERT INTO "SubscriptionTable" (user_id, start_date, end_date, plan_type)
            VALUES (:uid, :start, :end, :plan)
        """), {
            "uid": user_id,
            "start": datetime.utcnow(),
            "end": expiry_date,
            "plan": plan
        })
        db.commit()

        return {"status": "success", "message": f"{plan.replace('_', ' ').title()} plan activated"}

    return {"status": "ignored", "message": "Event not relevant"}
