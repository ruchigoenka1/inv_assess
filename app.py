import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Enterprise Inventory & Cash Manager", layout="wide")
st.title("📂 Comprehensive Inventory & Cash Flow Assessment")

# --- 2. INPUT SECTION (CREDIT & LOGISTICS) ---
with st.sidebar:
    st.header("Financial Parameters")
    # Your requested Input Boxes
    supplier_credit = st.number_input("Supplier Credit Terms (Days)", min_value=0, value=30, help="Days from dispatch to payment")
    customer_credit = st.number_input("Customer Credit Terms (Days)", min_value=0, value=15, help="Days from sale to receipt")
    
    st.header("Operational Timings")
    transit_days = st.number_input("Transit Duration (Days)", min_value=0, value=10)
    avg_days_in_stock = st.number_input("Avg. Days in Stock", min_value=0, value=45)

    st.header("Bulk Assessment Data")
    unit_cost = st.number_input("Unit Cost ($)", value=50.0)
    total_units = st.number_input("Total Inventory Units", value=1000)

# --- 3. CORE LOGIC & CALCULATIONS ---
# Base Timeline (Day 0 = Supplier Dispatch)
day_dispatch = 0
day_arrival = day_dispatch + transit_days
day_payment_to_supplier = day_dispatch + supplier_credit
day_sale = day_arrival + avg_days_in_stock
day_receipt_from_customer = day_sale + customer_credit

# Financial Metrics
total_outlay = unit_cost * total_units
cash_gap = day_receipt_from_customer - day_payment_to_supplier

# --- 4. PREPARING THE DATA FOR THE GRAPH ---
# We define specific phases to meet your color-coding requirements
timeline_data = [
    {
        "Phase": "In-Transit", 
        "Start": day_dispatch, 
        "End": day_arrival, 
        "State": "Physical Movement",
        "Color": "Orange",
        "Details": "Goods are with carrier"
    },
    {
        "Phase": "Physically in Store", 
        "Start": day_arrival, 
        "End": day_sale, 
        "State": "Inventory On-Hand",
        "Color": "Green",
        "Details": "Stock available for fulfillment"
    },
    {
        "Phase": "Receivable Period", 
        "Start": day_sale, 
        "End": day_receipt_from_customer, 
        "State": "Awaiting Payment",
        "Color": "Blue",
        "Details": "Goods delivered to customer"
    }
]

df = pd.DataFrame(timeline_data)

# --- 5. THE VISUALIZATION ---
# Using a Timeline chart to show the overlap of physical vs financial states
fig = px.timeline(
    df, 
    x_start="Start", 
    x_end="End", 
    y="Phase", 
    color="Phase",
    color_discrete_map={
        "In-Transit": "orange",
        "Physically in Store": "green",
        "Receivable Period": "royalblue"
    },
    title="End-to-End Inventory & Cash Cycle"
)

# Formatting X-axis to show Days instead of Dates
fig.layout.xaxis.type = 'linear'
for i in range(len(fig.data)):
    fig.data[i].x = [df.iloc[i]['End'] - df.iloc[i]['Start']]
    fig.data[i].base = [df.iloc[i]['Start']]

# Adding vertical markers for the actual Cash Movement
fig.add_vline(x=day_payment_to_supplier, line_dash="dash", line_color="red", 
              annotation_text=f"CASH OUT (Day {day_payment_to_supplier})", annotation_position="top left")

fig.add_vline(x=day_receipt_from_customer, line_dash="dash", line_color="gold", 
              annotation_text=f"CASH IN (Day {day_receipt_from_customer})", annotation_position="bottom right")

fig.update_layout(showlegend=False, height=400, xaxis_title="Days from Initial Order")

# --- 6. THE DASHBOARD VIEW ---
st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Order Value", f"${total_outlay:,.2f}")
with col2:
    st.metric("Cash Blocked Duration", f"{cash_gap} Days", delta=f"{cash_gap} days", delta_color="inverse")
with col3:
    status = "Negative Cash Cycle" if cash_gap > 0 else "Self-Financing Cycle"
    st.write(f"**Financial Status:** {status}")

# --- 7. DETAILED BREAKDOWN (Placeholder for your long original logic) ---
st.divider()
st.subheader("📋 Detailed Assessment Breakdown")
with st.expander("Click to see full inventory aging and cost analysis"):
    # This is where your "very long" logic from the original file should go
    st.write("Original Calculation Logic (Extended Version):")
    
    analysis_df = pd.DataFrame({
        "Event": ["Order Dispatched", "Payment to Supplier", "Arrival at Store", "Sale Date", "Payment Recieved"],
        "Day Count": [day_dispatch, day_payment_to_supplier, day_arrival, day_sale, day_receipt_from_customer],
        "Cash Impact": [0, -total_outlay, 0, 0, total_outlay]
    })
    st.table(analysis_df)

st.info("**Note:** If the Red Line (Cash Out) appears before the Green bar ends, you are paying for goods before they arrive.")
