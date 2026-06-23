import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.database import query_dataframe, execute_write
from src.ai_reports import generate_building_risk_explanation

# Verify session state
if 'df' not in st.session_state:
    st.switch_page("app.py")

df = st.session_state['df']

st.title("🏢 Individual Building Profile")
st.write("Drill down into a single asset's operational parameters, monthly energy history, and physical systems.")

# Building Selector
building_names = sorted(df['building_name'].tolist())
selected_b_name = st.selectbox("Select Building to Inspect", building_names)

# Extract building record from session state
b_row = df[df['building_name'] == selected_b_name].iloc[0]
b_id = b_row['building_id']

# Query building details from SQLite to demonstrate database connectivity
b_db_info = query_dataframe("SELECT * FROM buildings WHERE building_id = ?", (b_id,)).iloc[0]

# UI Columns for Profile Metadata
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Building Metadata")
    st.markdown(f"""
    *   **Building ID**: `{b_db_info['building_id']}`
    *   **Name**: **{b_db_info['building_name']}**
    *   **Type**: `{b_db_info['building_type']}`
    *   **Location**: `{b_db_info['city']}, {b_db_info['state']}`
    *   **Climate Zone**: `{b_db_info['climate_zone']}`
    *   **Year Built**: `{b_db_info['year_built']}`
    *   **Floor Area**: `{b_db_info['floor_area_sqft']:,.0f} sqft`
    *   **Number of Floors**: `{b_db_info['number_of_floors']}`
    *   **Occupancy Count**: `{b_db_info['occupancy_count']} persons`
    """)
    
    st.markdown("### Current Scores")
    
    r_cat = b_row['building_performance_risk_category']
    r_score = b_row['building_performance_risk_score']
    p_score = b_row['retrofit_priority_score']
    p_cat = b_row['retrofit_priority_category']
    star_score = b_row['energy_star_score']
    
    # Class style helper
    def get_class(cat):
        if cat in ['High', 'Critical']: return "badge-critical"
        if cat == 'Medium': return "badge-medium"
        return "badge-low"
        
    st.markdown(f"""
    *   **Energy Star Score**: `{star_score}/100`
    *   **Risk Level**: <span class="badge {get_class(r_cat)}">{r_cat} ({r_score:.1f})</span>
    *   **Retrofit Priority**: <span class="badge {get_class(p_cat)}">{p_cat} ({p_score:.1f})</span>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Annual Performance Indicators")
    
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric(label="Total Energy", value=f"{b_row['energy_use_kwh']:,.0f} kWh", delta=f"{b_row['eui']:.2f} EUI")
    with k2:
        st.metric(label="Total Operating Cost", value=f"${b_row['total_operating_cost']:,.2f}", delta=f"${b_row['cost_per_sqft']:.2f}/sqft")
    with k3:
        st.metric(label="Total Carbon Footprint", value=f"{b_row['carbon_emissions_kg']:,.0f} kg", delta=f"{b_row['carbon_intensity']:.2f} kg/sqft")

    # Retrofit Savings estimation details
    st.markdown("### Projected Retrofit Projections")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Est. Capital Cost", f"${b_row['estimated_retrofit_cost']:,.2f}")
    with s2:
        st.metric("Est. Cost Savings", f"${b_row['estimated_cost_savings']:,.2f}/yr")
    with s3:
        st.metric("Est. GHG Reduction", f"{b_row['estimated_carbon_reduction_kg']:,.0f} kg/yr")
    with s4:
        st.metric("Payback Period", f"{b_row['payback_period_years']:.1f} Yrs")

st.divider()

# Monthly Billing History Chart (Dynamic from DB)
st.subheader("🗓️ 2025 Monthly Billing & Consumption Trends")

monthly_df = query_dataframe("""
    SELECT month, electricity_cost, gas_cost, water_cost 
    FROM energy_records 
    WHERE building_id = ?
    ORDER BY month
""", (b_id,))

# Melt dataframe for easy Plotly mapping
melted_monthly = monthly_df.melt(
    id_vars=['month'], 
    value_vars=['electricity_cost', 'gas_cost', 'water_cost'],
    var_name='Utility Type',
    value_name='Cost ($)'
)
melted_monthly['Utility Type'] = melted_monthly['Utility Type'].str.replace('_cost', '').str.capitalize()

month_names = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}
melted_monthly['Month'] = melted_monthly['month'].map(month_names)

fig_monthly = px.bar(
    melted_monthly,
    x='Month',
    y='Cost ($)',
    color='Utility Type',
    title="Monthly Utility Operating Expenses ($)",
    labels={'Cost ($)': 'Cost ($)', 'Month': 'Month'},
    color_discrete_map={
        'Electricity': '#1abc9c',
        'Gas': '#e67e22',
        'Water': '#3498db'
    }
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()

# Equipment & Recommendations Details
ec1, ec2 = st.columns(2)

with ec1:
    st.subheader("🛠️ Building System Assets (SQLite)")
    equip_df = query_dataframe("""
        SELECT equipment_type, install_year, condition, last_service_date, estimated_replacement_cost
        FROM equipment
        WHERE building_id = ?
    """, (b_id,))
    
    st.dataframe(
        equip_df.style.format({
            'estimated_replacement_cost': '${:,.2f}'
        }),
        use_container_width=True
    )

with ec2:
    st.subheader("📋 Recommended Upgrades")
    recs_df = query_dataframe("""
        SELECT recommendation_type, estimated_cost, estimated_annual_savings, estimated_carbon_reduction
        FROM retrofit_recommendations
        WHERE building_id = ?
    """, (b_id,))
    
    st.dataframe(
        recs_df.style.format({
            'estimated_cost': '${:,.2f}',
            'estimated_annual_savings': '${:,.2f}',
            'estimated_carbon_reduction': '{:,.0f} kg'
        }),
        use_container_width=True
    )

st.divider()

# AI Assisted Summary Generation
st.subheader("🤖 AI-Assisted Performance Report")

# Check if report already exists in database
cached_report = query_dataframe("""
    SELECT generated_text 
    FROM ai_reports 
    WHERE building_id = ? AND report_type = 'Building Summary'
    ORDER BY report_id DESC LIMIT 1
""", (b_id,))

# Render generate button
if st.button("Generate Building Summary", key="gen_summary"):
    # Generate fresh summary (either rule-based fallback or OpenAI)
    summary = generate_building_risk_explanation(b_row)
    
    # Save to SQLite db
    execute_write(
        "INSERT INTO ai_reports (building_id, report_type, generated_text) VALUES (?, 'Building Summary', ?)",
        (b_id, summary)
    )
    
    st.success("Building summary generated successfully!")
    st.markdown(summary)
else:
    # Display cached report if it exists
    if not cached_report.empty:
        st.info("Displaying cached report. Click the button above to regenerate.")
        st.markdown(cached_report.iloc[0]['generated_text'])
    else:
        st.write("Click the button above to synthesize a customized performance evaluation report for this asset.")
