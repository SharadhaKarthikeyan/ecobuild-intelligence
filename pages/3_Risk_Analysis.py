import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.data_loader import load_building_data

# Verify session state
if 'df' not in st.session_state:
    st.switch_page("app.py")

df = st.session_state['df']

# Custom styling for card stats
st.markdown("""
<style>
    .card-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .risk-card {
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .low-card { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .med-card { background: linear-gradient(135deg, #f39c12, #f1c40f); }
    .high-card { background: linear-gradient(135deg, #d35400, #e67e22); }
    .crit-card { background: linear-gradient(135deg, #c0392b, #e74c3c); }
    
    .card-title { font-size: 0.9rem; text-transform: uppercase; opacity: 0.9; }
    .card-count { font-size: 2.2rem; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

st.title("⚠️ Operational Risk Analysis")
st.write("Drill down into the multi-factor building performance risk scores across the portfolio.")

# Calculate counts
low_c = len(df[df['building_performance_risk_category'] == 'Low'])
med_c = len(df[df['building_performance_risk_category'] == 'Medium'])
high_c = len(df[df['building_performance_risk_category'] == 'High'])
crit_c = len(df[df['building_performance_risk_category'] == 'Critical'])

# Display Risk Cards
st.markdown(f"""
<div class="card-grid">
    <div class="risk-card low-card">
        <div class="card-title">Low Risk (0-25)</div>
        <div class="card-count">{low_c}</div>
    </div>
    <div class="risk-card med-card">
        <div class="card-title">Medium Risk (26-50)</div>
        <div class="card-count">{med_c}</div>
    </div>
    <div class="risk-card high-card">
        <div class="card-title">High Risk (51-75)</div>
        <div class="card-count">{high_c}</div>
    </div>
    <div class="risk-card crit-card">
        <div class="card-title">Critical Risk (76-100)</div>
        <div class="card-count">{crit_c}</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Risk score distribution
    fig1 = px.histogram(
        df,
        x='building_performance_risk_score',
        color='building_performance_risk_category',
        nbins=30,
        title="Distribution of Building Risk Scores",
        labels={
            'building_performance_risk_score': 'Risk Score (0-100)',
            'building_performance_risk_category': 'Risk Level'
        },
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        }
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Risk by building type
    avg_risk_type = df.groupby('building_type')['building_performance_risk_score'].mean().reset_index()
    avg_risk_type = avg_risk_type.sort_values(by='building_performance_risk_score', ascending=False)
    
    fig2 = px.bar(
        avg_risk_type,
        x='building_type',
        y='building_performance_risk_score',
        labels={'building_performance_risk_score': 'Average Risk Score', 'building_type': 'Building Type'},
        title="Average Risk Score by Building Type",
        color='building_performance_risk_score',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # Risk by building age (Scatter plot)
    fig3 = px.scatter(
        df,
        x='building_age',
        y='building_performance_risk_score',
        color='building_performance_risk_category',
        hover_name='building_name',
        title="Building Age vs. Risk Score",
        labels={
            'building_age': 'Building Age (Years)',
            'building_performance_risk_score': 'Risk Score (0-100)',
            'building_performance_risk_category': 'Risk Level'
        },
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        }
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # Top 15 high-risk buildings
    top_risk = df.sort_values(by='building_performance_risk_score', ascending=False).head(15)
    
    fig4 = px.bar(
        top_risk,
        x='building_performance_risk_score',
        y='building_name',
        orientation='h',
        labels={'building_performance_risk_score': 'Risk Score', 'building_name': 'Building Name'},
        title="Top 15 Highest Risk Buildings",
        color='building_performance_risk_score',
        color_continuous_scale='reds'
    )
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Risk Factor Breakdown Table
st.subheader("High and Critical Risk Buildings Detail Table")

high_crit_df = df[df['building_performance_risk_category'].isin(['High', 'Critical'])].sort_values(
    by='building_performance_risk_score', ascending=False
)

columns_to_show = [
    'building_name', 'building_type', 'building_performance_risk_score',
    'building_performance_risk_category', 'eui', 'carbon_intensity', 'cost_per_sqft',
    'hvac_age', 'insulation_quality', 'years_since_retrofit', 'main_risk_reason'
]

# Apply styling mapping for categories
def highlight_risk(val):
    if val == 'Critical':
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
    elif val == 'High':
        return 'background-color: #ffe8d6; color: #d95d00; font-weight: bold;'
    return ''

st.dataframe(
    high_crit_df[columns_to_show].style.format({
        'building_performance_risk_score': '{:.1f}',
        'eui': '{:.2f}',
        'carbon_intensity': '{:.2f}',
        'cost_per_sqft': '${:.2f}',
        'years_since_retrofit': '{:d}'
    }).map(highlight_risk, subset=['building_performance_risk_category']),
    use_container_width=True
)
