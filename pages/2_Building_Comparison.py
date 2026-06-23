import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.data_loader import load_building_data

# Verify session state
if 'df' not in st.session_state:
    st.switch_page("app.py")

df = st.session_state['df']

st.title("⚖️ Building Benchmarking & Comparison")
st.write("Compare building subsets using filters to pinpoint poorly performing assets and outliers.")

# Sidebar filters specific to page 2 (in addition to main sidebar)
st.sidebar.markdown("### 🔍 Benchmark Filters")

# Building Type filter
all_types = sorted(df['building_type'].unique())
selected_types = st.sidebar.multiselect("Building Type", all_types, default=all_types)

# City filter
all_cities = sorted(df['city'].unique())
selected_cities = st.sidebar.multiselect("City", all_cities, default=all_cities)

# Climate Zone filter
all_climates = sorted(df['climate_zone'].unique())
selected_climates = st.sidebar.multiselect("Climate Zone", all_climates, default=all_climates)

# Year Built filter
min_year, max_year = int(df['year_built'].min()), int(df['year_built'].max())
selected_years = st.sidebar.slider("Year Built Range", min_year, max_year, (min_year, max_year))

# Risk Category filter
all_risks = sorted(df['building_performance_risk_category'].unique())
selected_risks = st.sidebar.multiselect("Risk Category", all_risks, default=all_risks)

# Energy Star Score filter
selected_star = st.sidebar.slider("Energy Star Score Range", 1, 100, (1, 100))

# Apply Filters
filtered_df = df[
    (df['building_type'].isin(selected_types)) &
    (df['city'].isin(selected_cities)) &
    (df['climate_zone'].isin(selected_climates)) &
    (df['year_built'].between(selected_years[0], selected_years[1])) &
    (df['building_performance_risk_category'].isin(selected_risks)) &
    (df['energy_star_score'].between(selected_star[0], selected_star[1]))
]

# Display data size
st.markdown(f"**Filtered Subset**: `{len(filtered_df)}` out of `{len(df)}` buildings.")

if filtered_df.empty:
    st.warning("No buildings match the selected filters. Please adjust the sidebar options.")
else:
    # 1. Bubble chart: floor area vs energy use, colored by risk category
    st.subheader("Asset Size vs. Energy Consumption")
    fig_bubble = px.scatter(
        filtered_df,
        x='floor_area_sqft',
        y='energy_use_kwh',
        size='occupancy_count',
        color='building_performance_risk_category',
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        },
        hover_name='building_name',
        labels={
            'floor_area_sqft': 'Floor Area (sqft)',
            'energy_use_kwh': 'Annual Energy Use (kWh)',
            'building_performance_risk_category': 'Risk Level'
        },
        title="Portfolio Building Envelope (Bubble size represents occupancy count)",
        log_x=True,
        log_y=True
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    st.divider()
    
    # 2. Comparative Distributions for EUI, Cost/Sqft, and Carbon Intensity
    st.subheader("Performance Metric Distributions")
    metric_choice = st.selectbox(
        "Choose Benchmarking Metric",
        ['Energy Use Intensity (EUI) (kWh/sqft)', 'Operating Cost per sqft ($/sqft)', 'Carbon Intensity (kg CO2e/sqft)']
    )
    
    col_map = {
        'Energy Use Intensity (EUI) (kWh/sqft)': 'eui',
        'Operating Cost per sqft ($/sqft)': 'cost_per_sqft',
        'Carbon Intensity (kg CO2e/sqft)': 'carbon_intensity'
    }
    target_col = col_map[metric_choice]
    
    c1, c2 = st.columns(2)
    
    with c1:
        # Boxplot grouped by building type
        fig_box = px.box(
            filtered_df,
            x='building_type',
            y=target_col,
            color='building_type',
            title=f"{metric_choice} Range by Building Type",
            labels={target_col: metric_choice, 'building_type': 'Building Type'}
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    with c2:
        # Histogram distribution
        fig_hist = px.histogram(
            filtered_df,
            x=target_col,
            color='building_performance_risk_category',
            color_discrete_map={
                'Low': '#2ecc71',
                'Medium': '#f1c40f',
                'High': '#e67e22',
                'Critical': '#e74c3c'
            },
            title=f"Frequency Distribution of {metric_choice}",
            labels={target_col: metric_choice, 'building_performance_risk_category': 'Risk Level'},
            marginal='rug'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
    st.divider()
    
    # 3. Energy Star Score Distribution
    st.subheader("Energy Star Score Distribution")
    fig_star = px.histogram(
        filtered_df,
        x='energy_star_score',
        nbins=20,
        color='building_type',
        title="Energy Star Score Distribution by Property Type",
        labels={'energy_star_score': 'Energy Star Score (1-100)'}
    )
    st.plotly_chart(fig_star, use_container_width=True)
    
    # 4. Outlier analysis / Poor performer list
    st.subheader("Pinpointed Poor Performers (Top 10 High EUI)")
    outliers = filtered_df.sort_values(by='eui', ascending=False).head(10)[
        ['building_name', 'building_type', 'city', 'state', 'eui', 'cost_per_sqft', 'carbon_intensity', 'energy_star_score', 'building_performance_risk_category']
    ]
    st.dataframe(
        outliers.style.format({
            'eui': '{:.2f}',
            'cost_per_sqft': '${:.2f}',
            'carbon_intensity': '{:.2f}'
        }).background_gradient(subset=['eui', 'cost_per_sqft', 'carbon_intensity'], cmap='Oranges'),
        use_container_width=True
    )
