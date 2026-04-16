import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION & AESTHETICS ---
st.set_page_config(page_title="Onyx Payment Hub", layout="wide")

# Custom CSS for the Onyx Dark Mode and Neon accents
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
    }
    h1, h2, h3, p {
        color: #F8F9FA;
    }
    .metric-value-blue {
        color: #00E5FF;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-value-purple {
        color: #B026FF;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-value-green {
        color: #39FF14;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #A0A0A0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Onyx Payment Hub: Arbitrage Tracker")
st.markdown("Monitoring the 36-month $0-down capital protection strategy.")
st.divider()

# --- SIDEBAR / CONTROLS ---
st.sidebar.header("Strategy Parameters")
hysa_replenishment = st.sidebar.slider(
    "Monthly HYSA Replenishment ($)", 
    min_value=400, max_value=800, value=560, step=10
)

# Constants based on the exact deal
loan_principal = 38500.00
loan_apr = 0.009
loan_months = 36
monthly_payment = 1084.31 

hysa_initial = 22000.00
hysa_apy = 0.0325

# --- AMORTIZATION ENGINE ---
months = []
loan_balances = []
hysa_balances = []
cumulative_loan_interest = []
cumulative_hysa_interest = []

current_loan = loan_principal
current_hysa = hysa_initial
total_loan_int = 0.0
total_hysa_int = 0.0

# Set the exact date of your first payment
start_date = pd.to_datetime("2026-05-15")

for i in range(loan_months):
    # Loan Math
    interest_payment = current_loan * (loan_apr / 12)
    principal_payment = monthly_payment - interest_payment
    current_loan -= principal_payment
    total_loan_int += interest_payment
    
    # HYSA Math (Subtract car payment, add replenishment, add interest)
    hysa_interest = current_hysa * (hysa_apy / 12)
    current_hysa = current_hysa - monthly_payment + hysa_replenishment + hysa_interest
    total_hysa_int += hysa_interest
    
    # Calculate the exact date for this specific month
    current_date = start_date + pd.DateOffset(months=i)
    
    # Store Data
    months.append(current_date.strftime('%b %d, %Y')) # Formats as "May 15, 2026"
    loan_balances.append(max(0, current_loan))
    hysa_balances.append(current_hysa)
    cumulative_loan_interest.append(total_loan_int)
    cumulative_hysa_interest.append(total_hysa_int)

# --- TOP COMMAND CENTER (WIDGETS) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<p class="metric-label">Projected HYSA Balance (Month 36)</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-blue">${hysa_balances[-1]:,.2f}</p>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="metric-label">Total Loan Interest Paid</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-purple">${total_loan_int:,.2f}</p>', unsafe_allow_html=True)

with col3:
    net_profit = total_hysa_int - total_loan_int
    st.markdown('<p class="metric-label">Net Arbitrage Profit</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-green">${net_profit:,.2f}</p>', unsafe_allow_html=True)

st.divider()

# --- CROSSOVER VISUALIZER (PLOTLY) ---
st.subheader("Capital Crossover Graph")
fig = go.Figure()

# Loan Line (Cyber Purple)
fig.add_trace(go.Scatter(
    x=months, y=loan_balances, mode='lines', 
    name='Auto Loan Balance', line=dict(color='#B026FF', width=3)
))

# HYSA Line (Electric Blue)
fig.add_trace(go.Scatter(
    x=months, y=hysa_balances, mode='lines', 
    name='HYSA Balance', line=dict(color='#00E5FF', width=3)
))

fig.update_layout(
    plot_bgcolor='#121212',
    paper_bgcolor='#121212',
    font=dict(color='#A0A0A0'),
    xaxis=dict(title="Payment Date", showgrid=False),
    yaxis=dict(title="Dollars ($)", showgrid=True, gridcolor='#333333', tickprefix="$"),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# --- PAYMENT HUB SCHEDULE ---
st.subheader("36-Month Amortization Schedule")

# Build the DataFrame
schedule_df = pd.DataFrame({
    "Payment Date": months,
    "Loan Balance": loan_balances,
    "Cumulative Loan Interest": cumulative_loan_interest,
    "HYSA Balance": hysa_balances,
    "Cumulative HYSA Interest": cumulative_hysa_interest,
    "Net Spread": [hysa - loan for hysa, loan in zip(cumulative_hysa_interest, cumulative_loan_interest)]
})

# Format for clean display
styled_df = schedule_df.style.format({
    "Loan Balance": "${:,.2f}",
    "Cumulative Loan Interest": "${:,.2f}",
    "HYSA Balance": "${:,.2f}",
    "Cumulative HYSA Interest": "${:,.2f}",
    "Net Spread": "${:,.2f}"
})

st.dataframe(styled_df, use_container_width=True, hide_index=True)
