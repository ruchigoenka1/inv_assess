import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="Inventory Cash Flow Pro", layout="wide")

st.title("📦 Inventory Assessment & Cash Flow Logic")
st.markdown("Track exactly when your cash is blocked based on supplier and customer credit terms.")

# --- Sidebar Inputs ---
st.sidebar.header("1. Supplier & Logistics")
transit_days = st.sidebar.number_input("Transit Time (Days)", min_value=0, value=10)
supplier_credit = st.sidebar.number_input("Credit by Supplier (Days from Dispatch)", min_value=0, value=15)

st.sidebar.header("2. Operations")
days_in_store = st.sidebar.number_input("Days Inventory Stays in Store", min_value=0, value=20)

st.sidebar.header("3. Customer Terms")
customer_credit = st.sidebar.number_input("Credit Given to Customer (Days from Sale)", min_value=0, value=30)

# --- Calculation Logic ---
# Milestones (Day 0 = Supplier Dispatches)
t_dispatch = 0
t_arrival = t_dispatch + transit_days
t_supplier_payment = t_dispatch + supplier_credit
t_sale = t_arrival + days_in_store
t_customer_payment = t_sale + customer_credit

# Cash Flow Status Logic
cash_blocked_duration = t_customer_payment - t_supplier_payment

# --- Data for Inventory Timeline ---
inv_data = [
    dict(Stage="Logistics", Start=t_dispatch, End=t_arrival, Status="In-Transit (Orange)", Desc="Goods traveling to you"),
    dict(Stage="Warehouse", Start=t_arrival, End=t_sale, Status="In-Store (Green)", Desc="Physically in your possession"),
    dict(Stage="Finance", Start=t_sale, End=t_customer_payment, Status="Receivable (Blue)", Desc="Waiting for customer cash")
]
df_inv = pd.DataFrame(inv_data)

# --- Visualization ---
fig = px.timeline(
    df_inv, 
    x_start="Start", 
    x_end="End", 
    y="Stage", 
    color="Status",
    hover_data=["Desc"],
    color_discrete_map={
        "In-Transit (Orange)": "#FFA500",
        "In-Store (Green)": "#2E8B57",
        "Receivable (Blue)": "#1E90FF"
    },
    title="Inventory & Receivable Lifecycle"
)

# Convert timeline to linear days
fig.layout.xaxis.type = 'linear'
for i in range(len(fig.data)):
    fig.data[i].x = [df_inv.iloc[i]['End'] - df_inv.iloc[i]['Start']]
    fig.data[i].base = [df_inv.iloc[i]['Start']]

# Add Cash Flow Markers
fig.add_vline(x=t_supplier_payment, line_dash="dash", line_color="red", 
              annotation_text="PAYMENT TO SUPPLIER", annotation_position="top left")
fig.add_vline(x=t_customer_payment, line_dash="dash", line_color="green", 
              annotation_text="CASH FROM CUSTOMER", annotation_position="bottom right")

# Highlight the "Cash Blocked" zone
fig.add_vrect(x0=t_supplier_payment, x1=t_customer_payment, 
              fillcolor="red", opacity=0.1, layer="below", line_width=0,
              annotation_text="CASH BLOCKED PERIOD", annotation_position="top center")

fig.update_layout(xaxis_title="Days", yaxis_title="", showlegend=True, height=500)

# --- Display Interface ---
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Cash Metrics")
    st.metric("Total Cycle Time", f"{t_customer_payment} Days")
    st.metric("Cash Blocked", f"{cash_blocked_duration} Days", delta=f"{cash_blocked_duration} days", delta_color="inverse")
    
    st.divider()
    
    if t_supplier_payment < t_arrival:
        st.error(f"**High Risk:** You pay the supplier on Day {t_supplier_payment}, but goods only arrive on Day {t_arrival}. You are financing the transit.")
    elif t_supplier_payment < t_sale:
        st.warning(f"**Moderate Risk:** You pay the supplier while goods are still sitting in your warehouse.")
    else:
        st.success("**Ideal:** You pay the supplier after you have already sold the goods!")

# --- Detailed Logic Table ---
with st.expander("View Daily Movement Details"):
    steps = {
        "Day 0": "Supplier dispatches the order.",
        f"Day {t_arrival}": "Material arrives at your premises (In-Store).",
        f"Day {t_supplier_payment}": "CASH OUT: Supplier credit expires. You must pay.",
        f"Day {t_sale}": "Sale made to customer. Material leaves warehouse.",
        f"Day {t_customer_payment}": "CASH IN: Customer credit expires. Cash received."
    }
    st.write(steps)
