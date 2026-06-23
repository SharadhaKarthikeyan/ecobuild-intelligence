import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.express as px
from src.data_loader import load_building_data
from src.data_cleaning import clean_and_map_columns
from src.metrics import calculate_derived_metrics
from src.risk_scoring import calculate_risk_scores
from src.retrofit import calculate_retrofit_priorities
from src.database import seed_db_from_dataframe, is_db_seeded

# Page config
st.set_page_config(
    page_title="EcoBuild Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom Professional Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .card {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        padding: 1.5rem;
        border: 1px solid #eaeaea;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-title {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 0.2rem;
    }
    
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
    }
    
    .badge-low { background-color: #d4edda; color: #155724; }
    .badge-medium { background-color: #fff3cd; color: #856404; }
    .badge-high { background-color: #ffe8d6; color: #d95d00; }
    .badge-critical { background-color: #f8d7da; color: #721c24; }
    
    .banner {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 25px rgba(30, 60, 114, 0.15);
    }
    
    .banner h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .banner p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to process and cache dataframe
def process_data(raw_df, status_msg):
    with st.spinner("Processing building metrics, risk scores, and retrofit priority..."):
        # 1. Clean and Map Columns
        cleaned_df = clean_and_map_columns(raw_df)
        
        # 2. Calculate Derived Metrics
        metrics_df = calculate_derived_metrics(cleaned_df)
        
        # 3. Calculate Risk Scoring
        risk_df = calculate_risk_scores(metrics_df)
        
        # 4. Calculate Retrofit Priorities & Savings
        final_df = calculate_retrofit_priorities(risk_df)
        
        # 5. Populate SQLite DB
        seed_db_from_dataframe(final_df)
        
        st.session_state['df'] = final_df
        st.session_state['data_status'] = status_msg
        return final_df

# Sidebar layout
st.sidebar.image("https://img.icons8.com/color/96/000000/green-home.png", width=80)
st.sidebar.markdown("### 📊 EcoBuild Navigation")
st.sidebar.markdown("""
Navigate pages using the sidebar menu above.
- **Portfolio Overview**: General KPIs & Charts
- **Building Comparison**: Interactive Benchmarking
- **Risk Analysis**: Heat maps & Risk rankings
- **Retrofit Prioritization**: CAPEX/OPEX savings
- **Carbon & Sustainability**: ESG goals
- **Building Profile**: Detailed tab for individual buildings
- **AI Assistant**: Natural Language Q&A
""")

st.sidebar.divider()
st.sidebar.markdown("### 📂 Data Pipeline Status")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload custom building CSV", type="csv")

# Initialize session state for dataset
if 'df' not in st.session_state or uploaded_file is not None:
    if uploaded_file is not None:
        raw_df, msg = load_building_data(uploaded_file)
        if raw_df is not None:
            df = process_data(raw_df, msg)
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
            # Load default if upload fails
            if 'df' not in st.session_state:
                raw_df, msg = load_building_data()
                df = process_data(raw_df, msg)
    else:
        # Load default
        raw_df, msg = load_building_data()
        df = process_data(raw_df, msg)
        st.sidebar.info(msg)
else:
    df = st.session_state['df']
    st.sidebar.success(st.session_state['data_status'])

# Main Page Layout
st.markdown("""
<div class="banner">
    <h1>EcoBuild Intelligence</h1>
    <p>Building Energy, Cost, Carbon, and Retrofit Analytics Platform</p>
</div>
""", unsafe_allow_html=True)

# Overview Columns
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### About the Platform")
    st.write(
        "EcoBuild Intelligence is a sophisticated decision-support platform designed to help facility managers, "
        "sustainability coordinators, and real estate investment trusts (REITs) optimize building operations. "
        "The platform processes utility billing records, equipment inventories, and architectural specs to rank "
        "buildings based on energy waste, operational cost risk, and carbon emissions. By applying predictive engineering "
        "models, the app suggests targeted energy-efficiency retrofits, estimates capital payback schedules, and generates "
        "interactive portfolio summaries."
    )
    
    st.markdown("#### Primary Capabilities")
    st.markdown("""
    - **Asset Benchmarking**: Compare Energy Use Intensity (EUI) and operating costs ($/sqft) across building types.
    - **Multi-Factor Risk Scoring**: Score buildings from 0 to 100 on energy, carbon, cost, and asset age.
    - **Retrofit Optimization**: Classify properties by retrofit feasibility, energy savings, and capital payback years.
    - **ESG Reporting**: Dynamic tracking of greenhouse gas emissions (GHG) and evolution of clean energy mix.
    - **AI Assistant**: Natural language querying over the portfolio to identify poor performers instantly.
    """)
    
    st.markdown("---")
    st.markdown("### Portfolio At-A-Glance")
    
    # KPI Grid
    k1, k2, k3 = st.columns(3)
    
    total_buildings = len(df)
    total_area = df['floor_area_sqft'].sum()
    avg_eui = df['eui'].mean()
    total_cost = df['total_operating_cost'].sum()
    avg_star = df['energy_star_score'].mean()
    total_carbon_mt = df['carbon_emissions_kg'].sum() / 1000.0
    
    with k1:
        st.markdown(f"""
        <div class="card">
            <div class="kpi-title">Buildings Managed</div>
            <div class="kpi-value">{total_buildings:,}</div>
            <div style="font-size:0.8rem; color:#27ae60;">Total Area: {total_area/1e6:.2f}M sqft</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="card">
            <div class="kpi-title">Annual Operating Cost</div>
            <div class="kpi-value">${total_cost/1e6:.2f}M</div>
            <div style="font-size:0.8rem; color:#7f8c8d;">Avg Cost: ${total_cost/total_area:.2f}/sqft</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="card">
            <div class="kpi-title">Total Emissions</div>
            <div class="kpi-value">{total_carbon_mt:,.1f} MT</div>
            <div style="font-size:0.8rem; color:#3498db;">Avg EUI: {avg_eui:.1f} kWh/sqft</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### Portfolio Risk & Prioritization Mix")
    
    # Risk Distribution Pie/Donut Chart
    risk_counts = df['building_performance_risk_category'].value_counts().reset_index()
    risk_counts.columns = ['Risk Category', 'Count']
    
    fig = px.pie(
        risk_counts, 
        values='Count', 
        names='Risk Category', 
        hole=0.5,
        color='Risk Category',
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        },
        title="Portfolio Buildings by Operational Risk"
    )
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Simple instructions banner
    st.info("👈 Use the page links in the sidebar to drill down into details, compare properties, or query the AI assistant.")
