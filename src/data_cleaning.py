import pandas as pd
import numpy as np

def clean_and_map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the building dataset and maps alternative column names to
    standard internal names. Also fills missing values using sensible fallbacks.
    """
    cleaned_df = df.copy()
    
    # Column mapping dictionary: alternative name -> standard internal name
    mapping = {
        'location_city': 'city',
        'location_state': 'state',
        'annual_operating_cost': 'total_operating_cost', # can map directly
        'operating_cost_per_sqft': 'cost_per_sqft',
        'emissions_intensity': 'carbon_intensity',
        'insulation_level': 'insulation_quality',
        'insulation_quality': 'insulation_quality',
        'renewable_energy_flag': 'renewable_energy_flag',
        'renewable_energy_pct': 'renewable_energy_pct',
        'last_retrofit_year': 'last_retrofit_year'
    }
    
    # Rename columns if they exist in mapping
    for old_col, new_col in mapping.items():
        if old_col in cleaned_df.columns and new_col not in cleaned_df.columns:
            cleaned_df = cleaned_df.rename(columns={old_col: new_col})
            
    # Specific conversion mappings for Mode 1:
    # 1. Convert annual_energy_use_kbtu to energy_use_kwh (1 kBTU = 0.293071 kWh)
    if 'annual_energy_use_kbtu' in cleaned_df.columns and 'energy_use_kwh' not in cleaned_df.columns:
        cleaned_df['energy_use_kwh'] = cleaned_df['annual_energy_use_kbtu'] * 0.293071
        
    # 2. Convert carbon_emissions_metric_tons to carbon_emissions_kg (1 Metric Ton = 1000 kg)
    if 'carbon_emissions_metric_tons' in cleaned_df.columns and 'carbon_emissions_kg' not in cleaned_df.columns:
        cleaned_df['carbon_emissions_kg'] = cleaned_df['carbon_emissions_metric_tons'] * 1000.0

    # Ensure required standard columns exist (if missing, initialize them)
    standard_columns_defaults = {
        'building_id': lambda df: [f"B{i+1:04d}" for i in range(len(df))],
        'building_name': lambda df: [f"Building {i+1}" for i in range(len(df))],
        'building_type': 'Mixed Use',
        'city': 'Unknown',
        'state': 'USA',
        'climate_zone': 'Mixed-Humid',
        'year_built': 1980,
        'floor_area_sqft': 50000,
        'number_of_floors': 3,
        'occupancy_count': 100,
        'energy_use_kwh': 100000.0,
        'water_use_gallons': 500000.0,
        'electricity_cost': 12000.0,
        'gas_cost': 4000.0,
        'maintenance_cost': 8000.0,
        'carbon_emissions_kg': 40000.0,
        'hvac_age': 12,
        'insulation_quality': 'Fair',
        'window_type': 'Double Pane',
        'energy_star_score': 50,
        'last_retrofit_year': lambda df: df['year_built'] if 'year_built' in df.columns else 1980,
        'renewable_energy_pct': 0.0,
        'estimated_retrofit_cost': lambda df: df['floor_area_sqft'] * 10.0 if 'floor_area_sqft' in df.columns else 500000.0
    }
    
    for col, default in standard_columns_defaults.items():
        if col not in cleaned_df.columns:
            if callable(default):
                cleaned_df[col] = default(cleaned_df)
            else:
                cleaned_df[col] = default
                
    # Data type cleaning and missing value filling
    cleaned_df['building_id'] = cleaned_df['building_id'].astype(str)
    cleaned_df['building_name'] = cleaned_df['building_name'].astype(str)
    cleaned_df['building_type'] = cleaned_df['building_type'].fillna('Mixed Use').astype(str)
    cleaned_df['city'] = cleaned_df['city'].fillna('Unknown').astype(str)
    cleaned_df['state'] = cleaned_df['state'].fillna('USA').astype(str)
    cleaned_df['climate_zone'] = cleaned_df['climate_zone'].fillna('Mixed-Humid').astype(str)
    
    cleaned_df['year_built'] = pd.to_numeric(cleaned_df['year_built'], errors='coerce').fillna(1980).astype(int)
    cleaned_df['floor_area_sqft'] = pd.to_numeric(cleaned_df['floor_area_sqft'], errors='coerce').fillna(50000.0).astype(float)
    cleaned_df['number_of_floors'] = pd.to_numeric(cleaned_df['number_of_floors'], errors='coerce').fillna(3).astype(int)
    cleaned_df['occupancy_count'] = pd.to_numeric(cleaned_df['occupancy_count'], errors='coerce').fillna(100).astype(int)
    
    cleaned_df['energy_use_kwh'] = pd.to_numeric(cleaned_df['energy_use_kwh'], errors='coerce').fillna(100000.0).astype(float)
    cleaned_df['water_use_gallons'] = pd.to_numeric(cleaned_df['water_use_gallons'], errors='coerce').fillna(500000.0).astype(float)
    
    cleaned_df['electricity_cost'] = pd.to_numeric(cleaned_df['electricity_cost'], errors='coerce').fillna(12000.0).astype(float)
    cleaned_df['gas_cost'] = pd.to_numeric(cleaned_df['gas_cost'], errors='coerce').fillna(4000.0).astype(float)
    cleaned_df['maintenance_cost'] = pd.to_numeric(cleaned_df['maintenance_cost'], errors='coerce').fillna(8000.0).astype(float)
    
    cleaned_df['carbon_emissions_kg'] = pd.to_numeric(cleaned_df['carbon_emissions_kg'], errors='coerce').fillna(40000.0).astype(float)
    cleaned_df['hvac_age'] = pd.to_numeric(cleaned_df['hvac_age'], errors='coerce').fillna(12).astype(int)
    cleaned_df['insulation_quality'] = cleaned_df['insulation_quality'].fillna('Fair').astype(str)
    cleaned_df['window_type'] = cleaned_df['window_type'].fillna('Double Pane').astype(str)
    cleaned_df['energy_star_score'] = pd.to_numeric(cleaned_df['energy_star_score'], errors='coerce').fillna(50).astype(int)
    cleaned_df['last_retrofit_year'] = pd.to_numeric(cleaned_df['last_retrofit_year'], errors='coerce').fillna(cleaned_df['year_built']).astype(int)
    cleaned_df['renewable_energy_pct'] = pd.to_numeric(cleaned_df['renewable_energy_pct'], errors='coerce').fillna(0.0).astype(float)
    cleaned_df['estimated_retrofit_cost'] = pd.to_numeric(cleaned_df['estimated_retrofit_cost'], errors='coerce').fillna(cleaned_df['floor_area_sqft'] * 10.0).astype(float)
    
    # Ensure sensible bounds on values
    cleaned_df['energy_use_kwh'] = cleaned_df['energy_use_kwh'].clip(lower=1.0)
    cleaned_df['floor_area_sqft'] = cleaned_df['floor_area_sqft'].clip(lower=1.0)
    cleaned_df['carbon_emissions_kg'] = cleaned_df['carbon_emissions_kg'].clip(lower=0.0)
    cleaned_df['energy_star_score'] = cleaned_df['energy_star_score'].clip(1, 100)
    
    return cleaned_df
