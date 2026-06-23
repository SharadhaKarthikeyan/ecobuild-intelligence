import os
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup OpenAI client conditionally
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key.strip() != "" and "your_api_key" not in openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
    except Exception:
        client = None
else:
    client = None

def generate_building_risk_explanation(building_row: pd.Series) -> str:
    """
    Generates a description explaining why a building is marked at its risk level,
    including contributing factors, recommended actions, and expected savings.
    """
    b_name = building_row['building_name']
    b_type = building_row['building_type']
    risk_score = building_row['building_performance_risk_score']
    risk_cat = building_row['building_performance_risk_category']
    eui = building_row['eui']
    carb_int = building_row['carbon_intensity']
    cost_sqft = building_row['cost_per_sqft']
    hvac_age = building_row['hvac_age']
    insulation = building_row['insulation_quality']
    windows = building_row['window_type']
    years_retrofit = building_row['years_since_retrofit']
    
    # Calculate some stats for comparison (could be passed in, or static averages)
    # Let's generate a narrative
    header = f"### Risk Analysis for {b_name} ({b_type})\n\n"
    header += f"**Risk Rating**: `{risk_cat} (Score: {risk_score}/100)`\n\n"
    
    body = "#### Key Risk Drivers:\n"
    drivers = []
    
    if eui > 25.0:
        drivers.append(f"- **High Energy Intensity**: The building's EUI is `{eui:.2f} kWh/sqft`, indicating high energy consumption relative to its footprint.")
    if carb_int > 10.0:
        drivers.append(f"- **High Carbon Intensity**: Emits `{carb_int:.2f} kg CO2e/sqft` annually, reflecting low energy efficiency or high carbon source fuel.")
    if cost_sqft > 3.0:
        drivers.append(f"- **Elevated Operating Expenses**: The operating cost is `{cost_sqft:.2f}/sqft` annually, driven by high utility and maintenance bills.")
    if hvac_age > 15:
        drivers.append(f"- **Aging HVAC Equipment**: The cooling/heating system is `{hvac_age} years old` (expected lifetime is ~15 years), leading to inefficiency and high maintenance costs.")
    if insulation in ['Poor', 'Fair']:
        drivers.append(f"- **Substandard Thermal Insulation**: The insulation is rated `{insulation}`, allowing significant thermal transfer and heating/cooling loss.")
    if windows == 'Single Pane':
        drivers.append(f"- **Inefficient Glazing**: Single-pane windows do not provide thermal barriers, causing HVAC strain.")
    if years_retrofit > 15:
        drivers.append(f"- **Lack of Recent Upgrades**: No major energy retrofits have been performed in `{years_retrofit} years`.")
        
    if not drivers:
        body += "No severe risk drivers identified. The building is operating within optimal parameters.\n\n"
    else:
        body += "\n".join(drivers) + "\n\n"
        
    # Recommendations
    body += "#### Recommended Intervention Roadmap:\n"
    recs = []
    if hvac_age > 15:
        recs.append("1. **High-Efficiency Heat Pump Retrofit**: Replace the aging system with a modern variable-refrigerant flow (VRF) heat pump system.")
    if windows == 'Single Pane':
        recs.append("2. **Window Glazing Upgrade**: Replace single-pane glass with modern low-E double or triple-pane glazed windows.")
    if insulation in ['Poor', 'Fair']:
        recs.append("3. **Building Envelope Weatherization**: Add insulation to roof spaces and fill wall cavities to reduce draft losses.")
    if building_row['renewable_energy_pct'] < 5.0:
        recs.append("4. **On-Site Solar PV Integration**: Consider installing rooftop solar arrays to supply clean electricity.")
    recs.append("5. **Smart Building Automation**: Implement smart thermostats and setback scheduling for off-hours.")
    
    body += "\n".join(recs) + "\n\n"
    
    # Savings
    savings_pct = building_row['estimated_energy_savings_kwh'] / building_row['energy_use_kwh'] * 100
    body += f"#### Financial & Environmental Savings Projections:\n"
    body += f"- **Estimated Energy Savings**: `{building_row['estimated_energy_savings_kwh']:,.0f} kWh/year` ({savings_pct:.0f}% reduction)\n"
    body += f"- **Estimated Cost Savings**: `${building_row['estimated_cost_savings']:,.2f}/year`\n"
    body += f"- **Carbon Footprint Reduction**: `{building_row['estimated_carbon_reduction_kg']:,.0f} kg CO2e/year`\n"
    body += f"- **Payback Period**: `{building_row['payback_period_years']:.1f} years` on an estimated retrofit capital expenditure of `${building_row['estimated_retrofit_cost']:,.2f}`.\n"
    
    if client is not None:
        try:
            prompt = f"""
            You are a building performance analyst. Based on this building data:
            Name: {b_name}
            Type: {b_type}
            Risk Score: {risk_score}
            Risk Category: {risk_cat}
            EUI: {eui:.2f} kWh/sqft
            Carbon Intensity: {carb_int:.2f} kg/sqft
            Operating Cost/sqft: {cost_sqft:.2f}
            HVAC Age: {hvac_age}
            Insulation: {insulation}
            Window: {windows}
            Years Since Retrofit: {years_retrofit}
            
            Generate a concise, professional executive risk explanation summary for a building dashboard.
            Keep it structured under:
            1. Risk Overview
            2. Contributing Risk Factors
            3. Target Recommended Actions
            4. Estimated Savings & Payback
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return header + body + f"\n*(AI Fallback: OpenAI query failed: {str(e)})*"
            
    return header + body

def generate_monthly_portfolio_report(df: pd.DataFrame) -> str:
    """
    Generates a monthly portfolio performance summary markdown text.
    """
    total_buildings = len(df)
    total_area = df['floor_area_sqft'].sum()
    total_energy = df['energy_use_kwh'].sum()
    total_cost = df['total_operating_cost'].sum()
    total_carbon = df['carbon_emissions_kg'].sum()
    avg_eui = df['eui'].mean()
    avg_cost = df['cost_per_sqft'].mean()
    
    critical_count = len(df[df['building_performance_risk_category'] == 'Critical'])
    high_count = len(df[df['building_performance_risk_category'] == 'High'])
    medium_count = len(df[df['building_performance_risk_category'] == 'Medium'])
    low_count = len(df[df['building_performance_risk_category'] == 'Low'])
    
    top_retrofit = df.sort_values(by='retrofit_priority_score', ascending=False).head(5)
    
    total_savings_cost = df['estimated_cost_savings'].sum()
    total_savings_carbon = df['estimated_carbon_reduction_kg'].sum()
    total_savings_energy = df['estimated_energy_savings_kwh'].sum()
    
    report_md = f"""# Monthly Building Performance Summary Report
**Date**: {datetime.now().strftime('%B %Y')}
**Author**: EcoBuild Analytics Engine

## 1. Executive Summary
This report summarizes the operational performance, carbon intensity, operational risk, and retrofit opportunities across the portfolio of **{total_buildings} buildings** totaling **{total_area:,.0f} square feet**.

### Portfolio KPIs:
*   **Total Portfolio Operating Cost**: ${total_cost:,.2f}
*   **Total Annual Energy Consumption**: {total_energy:,.0f} kWh
*   **Total Carbon Emissions**: {total_carbon/1000:,.1f} Metric Tons CO2e
*   **Average Energy Use Intensity (EUI)**: {avg_eui:.2f} kWh/sqft
*   **Average Cost per Square Foot**: ${avg_cost:.2f}/sqft

---

## 2. Operational Risk Profile
A multi-factor risk assessment has classified the portfolio into the following categories:
*   **Critical Risk**: `{critical_count} buildings` (Immediate action required)
*   **High Risk**: `{high_count} buildings`
*   **Medium Risk**: `{medium_count} buildings`
*   **Low Risk**: `{low_count} buildings`

The critical and high-risk buildings represent the largest source of cost and carbon inefficiencies due to aging HVAC systems, poor insulation, or extreme EUI metrics.

---

## 3. Top Retrofit Candidates & Prioritization
Based on composite risk scores and payback financials, the top 5 retrofit candidates are:

| Building Name | Type | Risk Category | Priority Score | Est. Cost | Est. Annual Savings | Payback Period (Yrs) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, row in top_retrofit.iterrows():
        report_md += f"| {row['building_name']} | {row['building_type']} | {row['building_performance_risk_category']} | {row['retrofit_priority_score']} | ${row['estimated_retrofit_cost']:,.2f} | ${row['estimated_cost_savings']:,.2f} | {row['payback_period_years']:.1f} |\n"
        
    report_md += f"""
---

## 4. Projected Retrofit Portfolio Benefits
By implementing the recommended energy efficiency measures across the entire portfolio, the following outcomes are projected:
*   **Annual Electricity/Gas Cost Savings**: `${total_savings_cost:,.2f}`
*   **Annual Carbon Reductions**: `{total_savings_carbon/1000:,.1f} Metric Tons CO2e` ({total_savings_carbon / max(1, total_carbon)*100:.1f}% Reduction)
*   **Annual Energy Usage Savings**: `{total_savings_energy:,.0f} kWh`

## 5. Next Steps & Recommended Actions
1.  **Conduct Detailed Site Audits** for the top 5 prioritized candidates.
2.  **Apply for Utility Rebates** and federal green building incentives for HVAC upgrades.
3.  **Commission HVAC Control Tuning** on all medium-risk office and school properties.
"""
    
    if client is not None:
        try:
            prompt = f"""
            You are a sustainability manager. Based on this portfolio summary:
            Total Buildings: {total_buildings}
            Total Sqft: {total_area:,.0f}
            Total Cost: ${total_cost:,.2f}
            Total Carbon: {total_carbon/1000:,.1f} Metric Tons
            Average EUI: {avg_eui:.2f} kWh/sqft
            Risk: {critical_count} Critical, {high_count} High, {medium_count} Medium, {low_count} Low
            Total Portfolio Retrofit Savings Potential: ${total_savings_cost:,.2f}/year, {total_savings_carbon/1000:,.1f} MT CO2/year
            
            Write a detailed executive monthly building energy and sustainability performance report. Make it sound professional, portfolio-ready, and analytical.
            Use clear headings, bullets, and tables where appropriate.
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return report_md + f"\n*(AI Fallback: OpenAI query failed: {str(e)})*"
            
    return report_md

def handle_assistant_query(query: str, df: pd.DataFrame) -> str:
    """
    Answers user natural language questions using the active building dataset.
    Has a robust rule-based parsing engine and an OpenAI engine fallback.
    """
    q = query.lower().strip()
    
    # 1. Retrofit Candidates First
    if "retrofit" in q and ("first" in q or "top" in q or "priority" in q or "candidate" in q):
        top_buildings = df.sort_values(by='retrofit_priority_score', ascending=False).head(5)
        res = "### Top 5 Buildings Recommended for Retrofits First:\n\n"
        res += "These buildings have been selected due to high risk scores, high EUI, and strong savings-to-cost potential.\n\n"
        res += "| Building Name | Type | Risk | Priority Score | Est. Savings ($/yr) | Payback (Years) |\n"
        res += "| :--- | :--- | :--- | :---: | :---: | :---: |\n"
        for _, row in top_buildings.iterrows():
            res += f"| {row['building_name']} | {row['building_type']} | {row['building_performance_risk_category']} | {row['retrofit_priority_score']} | ${row['estimated_cost_savings']:,.2f} | {row['payback_period_years']:.1f} |\n"
        return res
        
    # 2. Why is building X high risk?
    elif "why is" in q and ("risk" in q or "critical" in q):
        # Extract name if matches
        matched_row = None
        for _, row in df.iterrows():
            if row['building_name'].lower() in q:
                matched_row = row
                break
        if matched_row is None:
            # Let's pick a critical building to show as example
            crit_buildings = df[df['building_performance_risk_category'] == 'Critical']
            if not crit_buildings.empty:
                matched_row = crit_buildings.iloc[0]
                
        if matched_row is not None:
            return generate_building_risk_explanation(matched_row)
        else:
            return "I could not find a specific building matching that name in the dataset. Please verify the building name or check the 'Individual Building Profile' tab."

    # 3. Which building type has the highest carbon emissions?
    elif "building type" in q and ("carbon" in q or "emissions" in q or "highest" in q):
        emissions_by_type = df.groupby('building_type')['carbon_emissions_kg'].sum().reset_index()
        emissions_by_type = emissions_by_type.sort_values(by='carbon_emissions_kg', ascending=False)
        highest_type = emissions_by_type.iloc[0]
        
        res = "### Carbon Emissions Analysis by Building Type\n\n"
        res += f"The building type with the **highest total carbon emissions** is **{highest_type['building_type']}** "
        res += f"with a total of **{highest_type['carbon_emissions_kg']/1000:,.1f} Metric Tons CO2e** emitted annually.\n\n"
        res += "| Building Type | Total Carbon (Metric Tons) | Average Carbon Intensity (kg/sqft) |\n"
        res += "| :--- | :---: | :---: |\n"
        
        avg_int_by_type = df.groupby('building_type')['carbon_intensity'].mean().reset_index()
        for _, row in emissions_by_type.iterrows():
            avg_row = avg_int_by_type[avg_int_by_type['building_type'] == row['building_type']].iloc[0]
            res += f"| {row['building_type']} | {row['carbon_emissions_kg']/1000:,.1f} | {avg_row['carbon_intensity']:.2f} |\n"
        return res

    # 4. Generate monthly performance report
    elif "monthly" in q and "report" in q:
        return generate_monthly_portfolio_report(df)

    # 5. Top 5 actions to reduce cost
    elif "reduce cost" in q or "cost reduction" in q or "actions to reduce" in q:
        res = "### Top 5 Recommended Actions to Reduce Portfolio Operating Costs:\n\n"
        res += "1.  **HVAC Heat Pump Conversions**: Replacing systems older than 15 years with variable refrigerant flow heat pumps reduces energy costs by up to 25%.\n"
        res += "2.  **LED Lighting & Controls Retrofit**: Upgrading to LEDs with occupant sensors reduces electricity bills immediately and has a short (< 3 years) payback period.\n"
        res += "3.  **Envelope Weatherization (Insulation & Windows)**: Sealing drafts, updating insulation to Good/Excellent, and window glazing upgrades cuts down heating/cooling load significantly.\n"
        res += "4.  **Smart Building Energy Management System (BEMS)**: Implementing occupancy-based scheduling and setbacks during off-hours avoids wasted heating/cooling.\n"
        res += "5.  **Water Fixture Upgrades**: Installing low-flow fixtures and auditing for leaks reduces water expenses, which represents an under-optimized utility cost."
        return res

    # 6. Compare office and school buildings
    elif "office" in q and "school" in q and "compare" in q:
        offices = df[df['building_type'] == 'Office']
        schools = df[df['building_type'] == 'School']
        
        res = "### Building Type Comparison: Office vs. School\n\n"
        res += "| Performance Metric | Office (Avg) | School (Avg) |\n"
        res += "| :--- | :---: | :---: |\n"
        res += f"| Count | {len(offices)} | {len(schools)} |\n"
        res += f"| Floor Area (sqft) | {offices['floor_area_sqft'].mean():,.0f} | {schools['floor_area_sqft'].mean():,.0f} |\n"
        res += f"| Energy Use Intensity (EUI) (kWh/sqft) | {offices['eui'].mean():.2f} | {schools['eui'].mean():.2f} |\n"
        res += f"| Operating Cost per Sqft ($/sqft) | ${offices['cost_per_sqft'].mean():.2f} | ${schools['cost_per_sqft'].mean():.2f} |\n"
        res += f"| Carbon Intensity (kg/sqft) | {offices['carbon_intensity'].mean():.2f} | {schools['carbon_intensity'].mean():.2f} |\n"
        res += f"| Energy Star Score | {offices['energy_star_score'].mean():.1f} | {schools['energy_star_score'].mean():.1f} |\n"
        res += f"| Avg Risk Score (0-100) | {offices['building_performance_risk_score'].mean():.1f} | {schools['building_performance_risk_score'].mean():.1f} |\n"
        return res

    # 7. Which buildings have old HVAC systems?
    elif "hvac" in q and ("old" in q or "aging" in q or "system" in q):
        old_hvac = df[df['hvac_age'] > 15].sort_values(by='hvac_age', ascending=False)
        res = f"### Portfolio HVAC Age Analysis\n\n"
        res += f"Found **{len(old_hvac)} buildings** with HVAC systems exceeding the typical 15-year service life.\n\n"
        res += "| Building Name | Type | HVAC Age (Yrs) | Equipment Condition | Est. Replacement Cost |\n"
        res += "| :--- | :--- | :---: | :---: | :---: |\n"
        for _, row in old_hvac.head(10).iterrows():
            res += f"| {row['building_name']} | {row['building_type']} | {row['hvac_age']} | Poor | ${row['estimated_retrofit_cost']*0.6:,.2f} |\n"
        if len(old_hvac) > 10:
            res += f"\n*(Showing top 10 out of {len(old_hvac)} total old HVAC properties)*"
        return res

    # 8. Show critical-risk buildings built before 1990
    elif "before 1990" in q and ("critical" in q or "risk" in q):
        target = df[(df['year_built'] < 1990) & (df['building_performance_risk_category'] == 'Critical')]
        if target.empty:
            target = df[(df['year_built'] < 1990) & (df['building_performance_risk_category'] == 'High')]
            res = "### High-Risk Buildings Built Before 1990:\n*(No Critical-Risk properties met the exact age threshold)*\n\n"
        else:
            res = "### Critical-Risk Buildings Built Before 1990:\n\n"
            
        res += "| Building Name | Type | Built | Risk Score | EUI (kWh/sqft) | HVAC Age |\n"
        res += "| :--- | :--- | :---: | :---: | :---: | :---: |\n"
        for _, row in target.head(10).iterrows():
            res += f"| {row['building_name']} | {row['building_type']} | {row['year_built']} | {row['building_performance_risk_score']} | {row['eui']:.2f} | {row['hvac_age']} |\n"
        return res

    # Default chatbot fallback using OpenAI if available, else static summary
    if client is not None:
        try:
            total_b = len(df)
            avg_eui = df['eui'].mean()
            crit = len(df[df['building_performance_risk_category'] == 'Critical'])
            summary_info = f"Dataset size: {total_b} buildings. Average EUI: {avg_eui:.2f} kWh/sqft. Critical risk count: {crit} buildings."
            
            prompt = f"""
            You are EcoBuild Intelligence Assistant, an energy analytics chatbot.
            You help users query building data. Here is some high-level information about the active portfolio:
            {summary_info}
            
            The user asks: "{query}"
            
            Answer their query based strictly on building energy management, retrofit strategies, carbon reduction, and metrics.
            If they ask about details not supported by the data, provide a professional response guiding them back to building analytics.
            Keep your answer under 250 words and format in markdown.
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            pass
            
    # Default local markdown summary response
    res = "### EcoBuild Intelligence Portfolio Assistant\n\n"
    res += f"I am running in **local fallback mode** since no OpenAI API key is configured. I can answer standard queries using the dataset. Here is a summary of the active building portfolio:\n\n"
    res += f"*   **Total Buildings Managed**: {len(df)}\n"
    res += f"*   **Average Portfolio EUI**: {df['eui'].mean():.2f} kWh/sqft/year\n"
    res += f"*   **Critical Risk Buildings**: {len(df[df['building_performance_risk_category'] == 'Critical'])}\n"
    res += f"*   **Average Energy Star Score**: {df['energy_star_score'].mean():.1f}/100\n\n"
    res += "Try asking one of the standard portfolio questions below:\n"
    res += "- *Which buildings should be retrofitted first?*\n"
    res += "- *Which building type has the highest carbon emissions?*\n"
    res += "- *Which buildings have old HVAC systems?*\n"
    res += "- *Show critical-risk buildings built before 1990.*\n"
    return res
