import smtplib
import os
from datetime import date
from email.message import EmailMessage

# --- CONFIGURATION & SECRETS ---
SENDER_EMAIL = os.environ.get("EMAIL_SENDER")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD") # Use a Google App Password
RECEIVER_EMAILS = os.environ.get("EMAIL_RECEIVERS").split(",") # Comma-separated list

today = date.today()

# --- FINANCIAL ENGINE ---
loan_principal = 38500.00
monthly_payment = 1084.31
hysa_replenishment = 600.00 # Locked at the $600 target you established
loan_apr = 0.009
hysa_initial = 22000.00
hysa_apy = 0.0325
tax_rate = 0.33 # 24% Fed + 9% State

initial_vehicle_value = 35500.00
annual_depreciation_rate = 0.15

# Calculate current month offset (Starts May 2026)
months_passed = (today.year - 2026) * 12 + (today.month - 5)
if today.day >= 15:
    months_passed += 1

# Run the math up to the current month
current_loan = loan_principal
current_hysa = hysa_initial
current_vehicle = initial_vehicle_value
effective_apy = hysa_apy * (1 - tax_rate)

for _ in range(max(0, months_passed)):
    current_loan -= (monthly_payment - (current_loan * (loan_apr / 12)))
    current_hysa = current_hysa - monthly_payment + hysa_replenishment + (current_hysa * (effective_apy / 12))
    current_vehicle = current_vehicle * (1 - annual_depreciation_rate / 12)

# --- ALERT LOGIC ---
alerts_to_send = []

# 1. Pre-Payment Alert (10th of the month)
if today.day == 10:
    alerts_to_send.append(
        "Auto-Pay Warning: The $1,084.31 Subaru payment will be drawn from the Amex HYSA in 5 days. "
        f"Current estimated HYSA pool: ${current_hysa:,.2f}."
    )

# 2. Replenishment Alert (20th of the month)
if today.day == 20:
    alerts_to_send.append(
        f"Capital Replenishment: The auto-payment has cleared. Please ensure the target ${hysa_replenishment:,.0f} "
        "transfer from checking to the Amex HYSA is initiated to maintain the arbitrage spread."
    )

# 3. Equity Crossover Alert (Runs only on the 1st of the month to avoid spam)
if today.day == 1 and current_vehicle > current_loan:
    alerts_to_send.append(
        "EQUITY MILESTONE: The Forester is officially out of negative equity. "
        f"Estimated Vehicle Value: ${current_vehicle:,.2f} | Remaining Loan: ${current_loan:,.2f}."
    )

# 4. Capital Crossover Alert (Runs on the 1st)
if today.day == 1 and current_hysa > current_loan:
    alerts_to_send.append(
        "CAPITAL MILESTONE: Total liquid capital now exceeds total debt. "
        f"HYSA Balance: ${current_hysa:,.2f} | Remaining Loan: ${current_loan:,.2f}."
    )

# 5. Annual Insurance Audit (March 19th - 30 days before the April 18 purchase anniversary)
if today.month == 3 and today.day == 19:
    alerts_to_send.append(
        "STRATEGY AUDIT: The Forester's auto insurance policy is approaching renewal. "
        "It is time to re-shop the premium and verify the low-deductible Comprehensive glass coverage is still active."
    )

# --- EMAIL DISPATCHER ---
if alerts_to_send:
    msg = EmailMessage()
    msg['Subject'] = f"⚡ Onyx Hub Alert: {today.strftime('%b %d, %Y')}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAILS)
    
    body = "Hi Gabriel and Caitlynn,\n\nThe Onyx Payment Hub has generated the following strategic updates:\n\n"
    for idx, alert in enumerate(alerts_to_send, 1):
        body += f"{idx}. {alert}\n\n"
    body += "Keep executing the math.\n- The Onyx Engine"
    
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print("Alerts dispatched successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
else:
    print("No alerts triggered for today.")
