import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION & AESTHETICS ---
st.set_page_config(page_title="Onyx Payment Hub", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #121212; }
    h1, h2, h3, p { color: #F8F9FA; }
    .metric-value-blue { color: #00E5FF; font-size: 2.5rem; font-weight: bold; }
    .metric-value-purple { color: #B026FF; font-size: 2.5rem; font-weight: bold; }
    .metric-value-green { color: #39FF14; font-size: 2.5rem; font-weight: bold; }
    .metric-value-silver { color: #C0C0C0; font-size: 2.5rem; font-weight: bold; }
    .metric-label { font-size: 1.2rem; color: #A0A0A0; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Onyx Payment Hub: Arbitrage Tracker")
st.markdown("Monitoring the 36-month $0-down capital protection strategy.")
st.divider()

# --- SIDEBAR / CONTROLS ---
st.sidebar.header("Strategy Parameters")
hysa_replenishment = st.sidebar.slider(
    "Monthly HYSA Replenishment ($)", 
    min_value=450, max_value=650, value=600, step=10
)

st.sidebar.markdown("---")
st.sidebar.header("Tax Adjuster (Real Yield)")
fed_tax = st.sidebar.slider("Federal Tax Bracket (%)", min_value=10, max_value=37, value=24, step=2)
state_tax = st.sidebar.slider("State Tax Bracket (%)", min_value=0, max_value=13, value=9, step=1)

st.sidebar.markdown("---")
st.sidebar.header("Recovery Phase")
post_loan_replenishment = st.sidebar.slider(
    "Post-Loan Monthly Contribution ($)", 
    min_value=400, max_value=600, value=500, step=10
)

# --- CONSTANTS & CALCULATIONS ---
loan_principal = 38500.00
loan_apr = 0.009
loan_months = 36
monthly_payment = 1084.31 

hysa_initial = 22000.00
hysa_apy = 0.0325
tax_rate = (fed_tax + state_tax) / 100
effective_apy = hysa_apy * (1 - tax_rate)

initial_vehicle_value = 35500.00
annual_depreciation_rate = 0.15 

# --- AMORTIZATION ENGINE ---
months = []
loan_balances = []
hysa_balances = []
vehicle_values = []
cumulative_loan_interest = []
cumulative_hysa_interest_net = []

current_loan = loan_principal
current_hysa = hysa_initial
current_vehicle_value = initial_vehicle_value
total_loan_int = 0.0
total_hysa_int_net = 0.0

start_date = pd.to_datetime("2026-05-15")
equity_crossover_date = "Not Reached"
capital_crossover_date = "Not Reached"

for i in range(loan_months):
    # Loan Math
    interest_payment = current_loan * (loan_apr / 12)
    principal_payment = monthly_payment - interest_payment
    current_loan -= principal_payment
    total_loan_int += interest_payment
    
    # HYSA Math (After-Tax)
    hysa_interest_net = current_hysa * (effective_apy / 12)
    current_hysa = current_hysa - monthly_payment + hysa_replenishment + hysa_interest_net
    total_hysa_int_net += hysa_interest_net
    
    # Vehicle Depreciation
    current_vehicle_value = current_vehicle_value * (1 - annual_depreciation_rate / 12)
    
    # Store Data
    current_date = start_date + pd.DateOffset(months=i)
    formatted_date = current_date.strftime('%b %d, %Y')
    
    months.append(formatted_date)
    loan_balances.append(max(0, current_loan))
    hysa_balances.append(current_hysa)
    vehicle_values.append(current_vehicle_value)
    cumulative_loan_interest.append(total_loan_int)
    cumulative_hysa_interest_net.append(total_hysa_int_net)
    
    # Check Crossovers
    if current_loan < current_vehicle_value and equity_crossover_date == "Not Reached":
        equity_crossover_date = formatted_date
    if current_hysa > current_loan and capital_crossover_date == "Not Reached":
        capital_crossover_date = formatted_date

# --- STRATEGY KEY ---
st.info(f"""
**🔑 Core Blueprint**
* **Starting Capital Pool:** ${hysa_initial:,.2f}
* **Auto-Pay Draw:** ${monthly_payment:,.2f} (Executes on the 15th of every month)
* **Capital Crossover (HYSA > Debt):** {capital_crossover_date}
""")

# --- TOP COMMAND CENTER (WIDGETS) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<p class="metric-label">Final HYSA Pool</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-blue">${hysa_balances[-1]:,.2f}</p>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="metric-label">After-Tax Net Profit</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-green">${total_hysa_int_net - total_loan_int:,.2f}</p>', unsafe_allow_html=True)

with col3:
    st.markdown('<p class="metric-label">Interest Cost</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-purple">${total_loan_int:,.2f}</p>', unsafe_allow_html=True)

with col4:
    st.markdown('<p class="metric-label">Equity Crossover</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value-silver">{equity_crossover_date}</p>', unsafe_allow_html=True)

st.divider()

# --- CROSSOVER VISUALIZER ---
st.subheader("Capital & Equity Crossover Graph")
fig = go.Figure()

fig.add_trace(go.Scatter(x=months, y=loan_balances, name='Loan Balance', line=dict(color='#B026FF', width=3)))
fig.add_trace(go.Scatter(x=months, y=hysa_balances, name='HYSA Balance', line=dict(color='#00E5FF', width=3)))
fig.add_trace(go.Scatter(x=months, y=vehicle_values, name='Forester Value', line=dict(color='#C0C0C0', width=2, dash='dash')))

fig.update_layout(
    plot_bgcolor='#121212', paper_bgcolor='#121212', font=dict(color='#A0A0A0'),
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#333333', tickprefix="$"),
    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# --- AMORTIZATION TABLE (6-Month Scroll) ---
st.subheader("36-Month Amortization Schedule")
schedule_df = pd.DataFrame({
    "Payment Date": months,
    "Loan Balance": loan_balances,
    "Est. Car Value": vehicle_values,
    "HYSA Balance": hysa_balances,
    "After-Tax Net Spread": [hysa - loan for hysa, loan in zip(cumulative_hysa_interest_net, cumulative_loan_interest)]
})
styled_df = schedule_df.style.format({
    "Loan Balance": "${:,.2f}", "Est. Car Value": "${:,.2f}", 
    "HYSA Balance": "${:,.2f}", "After-Tax Net Spread": "${:,.2f}"
})
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=260)

# --- POST-LOAN RECOVERY TRACKER ---
st.divider()
st.subheader("Post-Loan Capital Recovery Tracker")
recovery_balance = hysa_balances[-1]
recovery_months = 0
recovery_date = pd.to_datetime(months[-1])

if recovery_balance < hysa_initial:
    while recovery_balance < hysa_initial and recovery_months < 120:
        recovery_interest = recovery_balance * (effective_apy / 12)
        recovery_balance += post_loan_replenishment + recovery_interest
        recovery_months += 1
        recovery_date += pd.DateOffset(months=1)

recovery_table = pd.DataFrame({
    "Strategic Metric": ["End of Loan HYSA", "Target Capital Pool", "Recovery Contribution", "Months to Recover", "Target Date"],
    "Projection": [f"${hysa_balances[-1]:,.2f}", f"${hysa_initial:,.2f}", f"${post_loan_replenishment:,.2f}", f"{recovery_months}", recovery_date.strftime('%b %d, %Y')]
})
st.table(recovery_table)
