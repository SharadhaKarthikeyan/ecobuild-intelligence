import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.data_loader import load_building_data
from src.data_cleaning import clean_and_map_columns
from src.metrics import calculate_derived_metrics
from src.risk_scoring import calculate_risk_scores
from src.retrofit import calculate_retrofit_priorities

# Verify session state data is present, else load
if 'df' not in st.session_state:
    raw_df, _ = load_building_data()
    cleaned = clean_and_map_columns(raw_df)
    metrics_df = calculate_derived_metrics(cleaned)
    risk_df = calculate_risk_scores(metrics_df)
    st.session_state['df'] = calculate_retrofit_priorities(risk_df)
    st.session_state['data_status'] = "Loaded default"

df = st.session_state['df']

# Custom styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        padding: 1.2rem;
        border: 1px solid #eaeaea;
        flex: 1 1 200px;
        min-width: 180px;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #7f8c8d;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Portfolio Overview Dashboard")
st.write("High-level key performance metrics and environmental distributions across the entire property portfolio.")

# Aggregate Metrics
total_b = len(df)
total_area = df['floor_area_sqft'].sum()
total_energy = df['energy_use_kwh'].sum()
total_cost = df['total_operating_cost'].sum()
total_carbon = df['carbon_emissions_kg'].sum()
avg_eui = df['eui'].mean()
avg_cost_sqft = df['cost_per_sqft'].mean()

critical_risk = len(df[df['building_performance_risk_category'] == 'Critical'])
high_risk = len(df[df['building_performance_risk_category'] == 'High'])
est_annual_savings = df['estimated_cost_savings'].sum()

# Render KPI Grid using Custom HTML for beautiful UI
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">Total Buildings</div>
        <div class="kpi-value">{total_b:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Total Area (sqft)</div>
        <div class="kpi-value">{total_area/1e6:.2f}M</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Annual Energy Use</div>
        <div class="kpi-value">{total_energy/1e6:.1f}M kWh</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Annual Utility Cost</div>
        <div class="kpi-value">${total_cost/1e6:.2f}M</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Carbon Footprint</div>
        <div class="kpi-value">{total_carbon/1e6:,.1f}k tons</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Portfolio EUI</div>
        <div class="kpi-value">{avg_eui:.1f}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Cost / sqft</div>
        <div class="kpi-value">${avg_cost_sqft:.2f}</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #e74c3c;">
        <div class="kpi-title" style="color: #e74c3c;">Critical Properties</div>
        <div class="kpi-value" style="color: #e74c3c;">{critical_risk}</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #e67e22;">
        <div class="kpi-title" style="color: #e67e22;">High Risk Properties</div>
        <div class="kpi-value" style="color: #e67e22;">{high_risk}</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #2ecc71;">
        <div class="kpi-title" style="color: #2ecc71;">Proj. Retrofit Savings</div>
        <div class="kpi-value" style="color: #2ecc71;">${est_annual_savings/1e6:.2f}M</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Charts Rows
r1_col1, r1_col2 = st.columns(2)

with r1_col1:
    # Energy use by building type
    energy_by_type = df.groupby('building_type')['energy_use_kwh'].sum().reset_index()
    energy_by_type = energy_by_type.sort_values(by='energy_use_kwh', ascending=False)
    energy_by_type['energy_use_mwh'] = energy_by_type['energy_use_kwh'] / 1000.0
    
    fig1 = px.bar(
        energy_by_type,
        x='building_type',
        y='energy_use_mwh',
        labels={'energy_use_mwh': 'Energy Consumed (MWh)', 'building_type': 'Building Type'},
        title="Annual Energy Consumption by Building Type (MWh)",
        color='energy_use_mwh',
        color_continuous_scale='tealgrn'
    )
    st.plotly_chart(fig1, use_container_width=True)

with r1_col2:
    # Carbon emissions by building type
    carbon_by_type = df.groupby('building_type')['carbon_emissions_kg'].sum().reset_index()
    carbon_by_type = carbon_by_type.sort_values(by='carbon_emissions_kg', ascending=False)
    carbon_by_type['carbon_emissions_tons'] = carbon_by_type['carbon_emissions_kg'] / 1000.0
    
    fig2 = px.bar(
        carbon_by_type,
        x='building_type',
        y='carbon_emissions_tons',
        labels={'carbon_emissions_tons': 'Carbon Emissions (Metric Tons)', 'building_type': 'Building Type'},
        title="Annual Carbon Emissions by Building Type (Metric Tons)",
        color='carbon_emissions_tons',
        color_continuous_scale='redor'
    )
    st.plotly_chart(fig2, use_container_width=True)

r2_col1, r2_col2 = st.columns(2)

with r2_col1:
    # Risk category distribution
    risk_dist = df['building_performance_risk_category'].value_counts().reset_index()
    risk_dist.columns = ['Risk Category', 'Count']
    
    fig3 = px.pie(
        risk_dist,
        values='Count',
        names='Risk Category',
        color='Risk Category',
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        },
        title="Portfolio Risk Classification Breakdown"
    )
    st.plotly_chart(fig3, use_container_width=True)

with r2_col2:
    # Top 10 highest energy buildings
    top_energy = df.sort_values(by='energy_use_kwh', ascending=False).head(10)
    top_energy['energy_use_mwh'] = top_energy['energy_use_kwh'] / 1000.0
    
    fig4 = px.bar(
        top_energy,
        x='energy_use_mwh',
        y='building_name',
        orientation='h',
        labels={'energy_use_mwh': 'Energy Consumed (MWh)', 'building_name': 'Building Name'},
        title="Top 10 Highest Energy Consuming Buildings",
        color='energy_use_mwh',
        color_continuous_scale='agsunset'
    )
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)
