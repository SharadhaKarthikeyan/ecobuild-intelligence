import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.data_loader import load_building_data

# Verify session state
if 'df' not in st.session_state:
    st.switch_page("app.py")

df = st.session_state['df']

# Custom styling for priority KPI cards
st.markdown("""
<style>
    .kpi-priorities {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .p-card {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        padding: 1.2rem;
        border: 1px solid #eaeaea;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .p-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }
    .p-title {
        font-size: 0.8rem;
        color: #7f8c8d;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .p-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔧 Retrofit Priority & Investment Analysis")
st.write("Prioritize capital expenditure (CAPEX) upgrades on properties with high operational risk and high return-on-investment (ROI).")

# High-level values
total_capex = df['estimated_retrofit_cost'].sum()
total_savings = df['estimated_cost_savings'].sum()
total_carbon_reduction = df['estimated_carbon_reduction_kg'].sum() / 1000.0 # metric tons
total_energy_savings = df['estimated_energy_savings_kwh'].sum()
portfolio_payback = total_capex / total_savings if total_savings > 0 else 0.0

# Render KPIs
st.markdown(f"""
<div class="kpi-priorities">
    <div class="p-card" style="border-top: 4px solid #2980b9;">
        <div class="p-title">Total CAPEX Required</div>
        <div class="p-value">${total_capex/1e6:.2f}M</div>
    </div>
    <div class="p-card" style="border-top: 4px solid #27ae60;">
        <div class="p-title">Est. Annual Cost Savings</div>
        <div class="p-value">${total_savings/1e6:.2f}M</div>
    </div>
    <div class="p-card" style="border-top: 4px solid #1abc9c;">
        <div class="p-title">Annual Energy Savings</div>
        <div class="p-value">{total_energy_savings/1e6:.1f}M kWh</div>
    </div>
    <div class="p-card" style="border-top: 4px solid #16a085;">
        <div class="p-title">Carbon Reductions</div>
        <div class="p-value">{total_carbon_reduction:,.1f} MT</div>
    </div>
    <div class="p-card" style="border-top: 4px solid #f39c12;">
        <div class="p-title">Weighted Payback</div>
        <div class="p-value">{portfolio_payback:.1f} Years</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Retrofit priority distribution
    priority_dist = df['retrofit_priority_category'].value_counts().reset_index()
    priority_dist.columns = ['Priority Category', 'Count']
    
    fig1 = px.pie(
        priority_dist,
        values='Count',
        names='Priority Category',
        color='Priority Category',
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        },
        title="Retrofit Priority Distribution across Portfolio"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Estimated cost savings by building type
    savings_by_type = df.groupby('building_type')['estimated_cost_savings'].sum().reset_index()
    savings_by_type = savings_by_type.sort_values(by='estimated_cost_savings', ascending=False)
    
    fig2 = px.bar(
        savings_by_type,
        x='building_type',
        y='estimated_cost_savings',
        labels={'estimated_cost_savings': 'Annual Cost Savings ($)', 'building_type': 'Building Type'},
        title="Projected Annual Financial Savings by Building Type",
        color='estimated_cost_savings',
        color_continuous_scale='greens'
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # Payback period by priority
    avg_payback_priority = df.groupby('retrofit_priority_category')['payback_period_years'].mean().reset_index()
    
    fig3 = px.bar(
        avg_payback_priority,
        x='retrofit_priority_category',
        y='payback_period_years',
        title="Average Payback Period (Years) by Priority Level",
        labels={'payback_period_years': 'Payback Period (Years)', 'retrofit_priority_category': 'Priority Category'},
        color='payback_period_years',
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # Top 10 retrofit candidates
    top_candidates = df.sort_values(by='retrofit_priority_score', ascending=False).head(10)
    
    fig4 = px.bar(
        top_candidates,
        x='retrofit_priority_score',
        y='building_name',
        orientation='h',
        labels={'retrofit_priority_score': 'Retrofit Priority Score', 'building_name': 'Building Name'},
        title="Top 10 Retrofit Priority Candidates",
        color='retrofit_priority_score',
        color_continuous_scale='viridis'
    )
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Retrofit Candidate Table
st.subheader("Top Retrofit Candidates Priority List")

priority_candidates = df.sort_values(by='retrofit_priority_score', ascending=False)

columns_to_show = [
    'building_name', 'building_type', 'building_performance_risk_category',
    'retrofit_priority_score', 'retrofit_priority_category',
    'estimated_retrofit_cost', 'estimated_cost_savings',
    'estimated_carbon_reduction_kg', 'payback_period_years'
]

def highlight_priority(val):
    if val == 'Critical':
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
    elif val == 'High':
        return 'background-color: #ffe8d6; color: #d95d00; font-weight: bold;'
    return ''

st.dataframe(
    priority_candidates[columns_to_show].style.format({
        'retrofit_priority_score': '{:.1f}',
        'estimated_retrofit_cost': '${:,.2f}',
        'estimated_cost_savings': '${:,.2f}',
        'estimated_carbon_reduction_kg': '{:,.0f} kg',
        'payback_period_years': '{:.1f} years'
    }).map(highlight_priority, subset=['retrofit_priority_category']),
    use_container_width=True
)
