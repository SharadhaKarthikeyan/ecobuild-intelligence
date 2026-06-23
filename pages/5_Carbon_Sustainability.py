import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.data_loader import load_building_data

# Verify session state
if 'df' not in st.session_state:
    st.switch_page("app.py")

df = st.session_state['df']

# Custom styling for ESG KPI cards
st.markdown("""
<style>
    .esg-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .esg-card {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        padding: 1.2rem;
        border: 1px solid #eaeaea;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .esg-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }
    .esg-title {
        font-size: 0.8rem;
        color: #7f8c8d;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .esg-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2e7d32;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍀 Carbon & Sustainability Analytics")
st.write("Track greenhouse gas (GHG) footprint, carbon intensity, renewable energy adoption, and ESG portfolio objectives.")

# Calculate sustainability stats
total_carbon = df['carbon_emissions_kg'].sum() / 1000.0 # metric tons
avg_intensity = df['carbon_intensity'].mean() # kg/sqft
renewables_adoption = len(df[df['renewable_energy_pct'] > 0.0])
avg_renewables_pct = df['renewable_energy_pct'].mean()
carbon_reduction_potential = df['estimated_carbon_reduction_kg'].sum() / 1000.0 # metric tons

# Render KPIs
st.markdown(f"""
<div class="esg-grid">
    <div class="esg-card" style="border-top: 4px solid #1b5e20;">
        <div class="esg-title">Total GHG Emissions</div>
        <div class="esg-value">{total_carbon:,.1f} MT CO2e</div>
    </div>
    <div class="esg-card" style="border-top: 4px solid #2e7d32;">
        <div class="esg-title">Avg Carbon Intensity</div>
        <div class="esg-value">{avg_intensity:.2f} kg/sqft</div>
    </div>
    <div class="esg-card" style="border-top: 4px solid #4caf50;">
        <div class="esg-title">Renewable Penetration</div>
        <div class="esg-value">{renewables_adoption} / {len(df)} Buildings</div>
        <div style="font-size:0.8rem; color:#7f8c8d;">Avg Renewable Share: {avg_renewables_pct:.1f}%</div>
    </div>
    <div class="esg-card" style="border-top: 4px solid #81c784;">
        <div class="esg-title">Carbon Reduction Potential</div>
        <div class="esg-value">{carbon_reduction_potential:,.1f} MT CO2e</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Carbon emissions by building type (Pie)
    carbon_by_type = df.groupby('building_type')['carbon_emissions_kg'].sum().reset_index()
    carbon_by_type.columns = ['Building Type', 'Carbon Emissions (kg)']
    carbon_by_type['Carbon Emissions (Metric Tons)'] = carbon_by_type['Carbon Emissions (kg)'] / 1000.0
    
    fig1 = px.pie(
        carbon_by_type,
        values='Carbon Emissions (Metric Tons)',
        names='Building Type',
        title="Distribution of Carbon Emissions by Building Type",
        color_discrete_sequence=px.colors.qualitative.Dark2
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Top 10 carbon-intensive buildings
    top_carb_intensive = df.sort_values(by='carbon_intensity', ascending=False).head(10)
    
    fig2 = px.bar(
        top_carb_intensive,
        x='carbon_intensity',
        y='building_name',
        orientation='h',
        labels={'carbon_intensity': 'Carbon Intensity (kg CO2e/sqft)', 'building_name': 'Building Name'},
        title="Top 10 Carbon Intensive Buildings (kg CO2e/sqft)",
        color='carbon_intensity',
        color_continuous_scale='reds'
    )
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # Renewable energy percentage distribution (histogram)
    # Only plot for buildings that actually have solar/renewables to make the chart meaningful
    renew_df = df[df['renewable_energy_pct'] > 0.0]
    
    fig3 = px.histogram(
        renew_df,
        x='renewable_energy_pct',
        nbins=15,
        color='building_type',
        title="Renewable Energy Adoption Share (%)",
        labels={'renewable_energy_pct': 'Renewable Energy % of Total Consumption'}
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # Carbon intensity vs EUI scatter plot
    fig4 = px.scatter(
        df,
        x='eui',
        y='carbon_intensity',
        color='building_type',
        size='floor_area_sqft',
        hover_name='building_name',
        title="Carbon Intensity vs. Energy Use Intensity (EUI)",
        labels={
            'eui': 'Energy Use Intensity (EUI) (kWh/sqft)',
            'carbon_intensity': 'Carbon Intensity (kg CO2e/sqft)',
            'building_type': 'Building Type'
        }
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Top Carbon Impact properties list
st.subheader("Top Carbon Emitting Properties (Top 10 Absolute Emissions)")
top_emitters = df.sort_values(by='carbon_emissions_kg', ascending=False).head(10)[
    ['building_name', 'building_type', 'city', 'state', 'carbon_emissions_kg', 'carbon_intensity', 'renewable_energy_pct', 'building_performance_risk_category']
]
top_emitters['carbon_emissions_tons'] = top_emitters['carbon_emissions_kg'] / 1000.0

st.dataframe(
    top_emitters[['building_name', 'building_type', 'city', 'state', 'carbon_emissions_tons', 'carbon_intensity', 'renewable_energy_pct', 'building_performance_risk_category']].style.format({
        'carbon_emissions_tons': '{:.1f} MT',
        'carbon_intensity': '{:.2f} kg/sqft',
        'renewable_energy_pct': '{:.1f}%'
    }).background_gradient(subset=['carbon_emissions_tons', 'carbon_intensity'], cmap='Reds'),
    use_container_width=True
)
