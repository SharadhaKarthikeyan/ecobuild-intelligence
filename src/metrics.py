import pandas as pd
import numpy as np

CURRENT_YEAR = 2026

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates derived building performance metrics from standard columns.
    Ensures safe operations (e.g. avoiding division by zero).
    """
    metrics_df = df.copy()
    
    # 1. Energy Use Intensity (EUI) (kWh/sqft)
    metrics_df['eui'] = metrics_df['energy_use_kwh'] / metrics_df['floor_area_sqft']
    
    # 2. Total Operating Cost (if not already present and populated)
    # If the user uploaded a file with a pre-populated total_operating_cost, we preserve it.
    if 'total_operating_cost' not in df.columns or df['total_operating_cost'].isna().all() or (df['total_operating_cost'] == 0).all():
        metrics_df['total_operating_cost'] = (
            metrics_df['electricity_cost'] + 
            metrics_df['gas_cost'] + 
            metrics_df['maintenance_cost']
        )
    else:
        metrics_df['total_operating_cost'] = df['total_operating_cost']
        
    # 3. Cost per Square Foot
    metrics_df['cost_per_sqft'] = metrics_df['total_operating_cost'] / metrics_df['floor_area_sqft']
    
    # 4. Carbon Intensity (kg CO2e/sqft)
    metrics_df['carbon_intensity'] = metrics_df['carbon_emissions_kg'] / metrics_df['floor_area_sqft']
    
    # 5. Building Age
    metrics_df['building_age'] = CURRENT_YEAR - metrics_df['year_built']
    # Clip building age to 0
    metrics_df['building_age'] = metrics_df['building_age'].clip(lower=0)
    
    # 6. Years Since Retrofit
    metrics_df['years_since_retrofit'] = CURRENT_YEAR - metrics_df['last_retrofit_year']
    metrics_df['years_since_retrofit'] = metrics_df['years_since_retrofit'].clip(lower=0)
    
    # 7. Energy Cost Ratio (Energy Cost / Total Operating Cost)
    energy_cost = metrics_df['electricity_cost'] + metrics_df['gas_cost']
    metrics_df['energy_cost_ratio'] = np.where(
        metrics_df['total_operating_cost'] > 0,
        energy_cost / metrics_df['total_operating_cost'],
        0.0
    )
    # Clip energy cost ratio between 0 and 1
    metrics_df['energy_cost_ratio'] = metrics_df['energy_cost_ratio'].clip(0.0, 1.0)
    
    return metrics_df
