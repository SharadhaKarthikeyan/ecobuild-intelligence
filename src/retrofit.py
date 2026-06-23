import pandas as pd
import numpy as np

def calculate_retrofit_priorities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates estimated savings and retrofit priority scores:
    - Low Risk: 5% savings
    - Medium Risk: 10% savings
    - High Risk: 18% savings
    - Critical Risk: 25% savings
    
    Priority formula:
    retrofit_priority_score = 0.40 * risk_score 
                              + 0.25 * potential_energy_savings_score 
                              + 0.20 * carbon_reduction_score 
                              + 0.15 * cost_savings_score
    """
    retrofit_df = df.copy()
    
    # 1. Map savings percentage based on risk category
    savings_mapping = {
        'Low': 0.05,
        'Medium': 0.10,
        'High': 0.18,
        'Critical': 0.25
    }
    
    # Fill in a default of 0.10 if something is wrong
    savings_pct = retrofit_df['building_performance_risk_category'].map(savings_mapping).fillna(0.10)
    
    # 2. Calculate savings metrics
    retrofit_df['estimated_energy_savings_kwh'] = retrofit_df['energy_use_kwh'] * savings_pct
    
    # Annual energy cost is electricity + gas cost
    annual_energy_cost = retrofit_df['electricity_cost'] + retrofit_df['gas_cost']
    # Fallback to 80% of total operating cost if energy costs are zero
    annual_energy_cost = np.where(
        annual_energy_cost > 0,
        annual_energy_cost,
        retrofit_df['total_operating_cost'] * 0.8
    )
    
    retrofit_df['estimated_cost_savings'] = annual_energy_cost * savings_pct
    retrofit_df['estimated_carbon_reduction_kg'] = retrofit_df['carbon_emissions_kg'] * savings_pct
    
    # Payback period: retrofit_cost / cost_savings
    retrofit_df['payback_period_years'] = np.where(
        retrofit_df['estimated_cost_savings'] > 0,
        retrofit_df['estimated_retrofit_cost'] / retrofit_df['estimated_cost_savings'],
        99.0
    ).round(2)
    
    # Clip payback period to a realistic max of 99.0 years
    retrofit_df['payback_period_years'] = retrofit_df['payback_period_years'].clip(0.0, 99.0)
    
    # 3. Calculate scores for priority (scaled 0-100)
    # Energy savings score based on EUI savings (kwh/sqft)
    eui_savings = retrofit_df['estimated_energy_savings_kwh'] / retrofit_df['floor_area_sqft']
    min_eui_sav, max_eui_sav = eui_savings.min(), eui_savings.max()
    energy_savings_score = np.where(
        max_eui_sav > min_eui_sav,
        (eui_savings - min_eui_sav) / (max_eui_sav - min_eui_sav) * 100,
        50.0
    )
    
    # Carbon reduction score based on carbon intensity reduction (kg/sqft)
    carb_sav_intensity = retrofit_df['estimated_carbon_reduction_kg'] / retrofit_df['floor_area_sqft']
    min_carb_sav, max_carb_sav = carb_sav_intensity.min(), carb_sav_intensity.max()
    carbon_reduction_score = np.where(
        max_carb_sav > min_carb_sav,
        (carb_sav_intensity - min_carb_sav) / (max_carb_sav - min_carb_sav) * 100,
        50.0
    )
    
    # Cost savings score based on cost savings per sqft ($/sqft)
    cost_sav_sqft = retrofit_df['estimated_cost_savings'] / retrofit_df['floor_area_sqft']
    min_cost_sav, max_cost_sav = cost_sav_sqft.min(), cost_sav_sqft.max()
    cost_savings_score = np.where(
        max_cost_sav > min_cost_sav,
        (cost_sav_sqft - min_cost_sav) / (max_cost_sav - min_cost_sav) * 100,
        50.0
    )
    
    # Calculate composite priority score
    risk_score = retrofit_df['building_performance_risk_score']
    
    priority_score = (
        0.40 * risk_score +
        0.25 * energy_savings_score +
        0.20 * carbon_reduction_score +
        0.15 * cost_savings_score
    ).round(1)
    
    retrofit_df['retrofit_priority_score'] = priority_score
    
    # Categorize retrofit priority
    conditions = [
        (retrofit_df['retrofit_priority_score'] <= 25),
        (retrofit_df['retrofit_priority_score'] <= 50),
        (retrofit_df['retrofit_priority_score'] <= 75),
        (retrofit_df['retrofit_priority_score'] > 75)
    ]
    categories = ['Low', 'Medium', 'High', 'Critical']
    retrofit_df['retrofit_priority_category'] = np.select(conditions, categories, default='Medium')
    
    return retrofit_df
