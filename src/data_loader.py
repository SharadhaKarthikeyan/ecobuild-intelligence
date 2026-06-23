import os
import pandas as pd
import numpy as np

def generate_synthetic_data(file_path: str, num_records: int = 2500) -> pd.DataFrame:
    """
    Generates a realistic building energy, cost, carbon, and retrofit dataset.
    """
    np.random.seed(42)
    
    # Building types and area parameters (min, max in sqft)
    building_types = {
        'Office': (20000, 250000, 18.0, 32.0),
        'School': (15000, 120000, 12.0, 24.0),
        'Hospital': (80000, 500000, 45.0, 90.0),
        'Residential': (10000, 150000, 10.0, 20.0),
        'Retail': (5000, 80000, 15.0, 35.0),
        'Lab': (20000, 180000, 60.0, 130.0),
        'Government': (15000, 200000, 16.0, 30.0),
        'Mixed Use': (30000, 300000, 18.0, 35.0)
    }
    
    cities_states = [
        ('New York', 'NY', 'Cold-Humid'),
        ('Chicago', 'IL', 'Cold-Humid'),
        ('Los Angeles', 'CA', 'Marine-Mild'),
        ('Houston', 'TX', 'Hot-Humid'),
        ('Phoenix', 'AZ', 'Hot-Dry'),
        ('Seattle', 'WA', 'Marine-Mild'),
        ('Atlanta', 'GA', 'Mixed-Humid'),
        ('Denver', 'CO', 'Cold-Dry')
    ]
    
    insulation_choices = ['Poor', 'Fair', 'Good', 'Excellent']
    window_choices = ['Single Pane', 'Double Pane', 'Triple Pane']
    
    data = []
    current_year = 2026
    
    for i in range(num_records):
        b_id = f"B{i+1:04d}"
        b_type = np.random.choice(list(building_types.keys()))
        min_area, max_area, min_eui, max_eui = building_types[b_type]
        
        # Floor area and floors
        area = int(np.random.uniform(min_area, max_area))
        num_floors = max(1, int(np.sqrt(area) / np.random.uniform(20, 40)))
        
        # Location
        loc_idx = np.random.choice(len(cities_states))
        city, state, climate = cities_states[loc_idx]
        
        # Name
        b_name = f"{city} {b_type} {np.random.randint(10, 99)}"
        
        # Year built
        year_built = int(np.random.uniform(1930, 2018))
        
        # Occupancy
        occupancy = max(5, int(area / np.random.uniform(150, 400)))
        
        # HVAC system age and retrofit status
        hvac_age = int(np.random.uniform(1, 25))
        last_retrofit = int(np.random.uniform(max(year_built, 1990), current_year))
        # Sometimes buildings have never been retrofitted
        if np.random.rand() < 0.2:
            last_retrofit = year_built
            
        insulation = np.random.choice(insulation_choices, p=[0.2, 0.3, 0.4, 0.1])
        window = np.random.choice(window_choices, p=[0.25, 0.55, 0.20])
        
        # Energy Star Score (negatively correlated with HVAC age and poor insulation)
        base_score = 75 - (hvac_age * 1.2)
        if insulation == 'Poor': base_score -= 15
        elif insulation == 'Excellent': base_score += 15
        if window == 'Single Pane': base_score -= 10
        elif window == 'Triple Pane': base_score += 10
        energy_star = int(np.clip(base_score + np.random.normal(0, 8), 1, 100))
        
        # Energy Use (kWh/year) - based on EUI and floor area
        # Apply scaling based on envelope quality
        eui_scaler = 1.0
        if insulation == 'Poor': eui_scaler += 0.20
        elif insulation == 'Excellent': eui_scaler -= 0.15
        if window == 'Single Pane': eui_scaler += 0.10
        elif window == 'Triple Pane': eui_scaler -= 0.08
            
        eui = np.random.uniform(min_eui, max_eui) * eui_scaler
        energy_use_kwh = area * eui
        
        # Water use
        water_use_gallons = area * np.random.uniform(10, 28)
        
        # Costs
        # Electricity is ~70% of energy usage, gas is ~30%
        electricity_kwh = energy_use_kwh * 0.70
        gas_kwh_equiv = energy_use_kwh * 0.30
        
        # Rates: Elec = $0.15/kWh, Gas = $0.06/kWh equiv, Water = $0.008/gallon
        electricity_cost = electricity_kwh * np.random.uniform(0.12, 0.18)
        gas_cost = gas_kwh_equiv * np.random.uniform(0.05, 0.08)
        water_cost = water_use_gallons * np.random.uniform(0.006, 0.010)
        
        # Maintenance cost
        maintenance_cost = area * np.random.uniform(1.20, 3.80)
        
        # Carbon emissions: Elec = 0.38 kg CO2e/kWh, Gas = 0.18 kg CO2e/kWh
        carbon_emissions_kg = (electricity_kwh * 0.38) + (gas_kwh_equiv * 0.18)
        
        # Renewable energy percentage
        renewable_energy_pct = 0.0
        if np.random.rand() < 0.25: # 25% of buildings have some renewables
            renewable_energy_pct = np.clip(np.random.exponential(12.0), 0.0, 100.0)
            # Offset emissions slightly
            carbon_emissions_kg *= (1.0 - (renewable_energy_pct / 100.0))
            
        # Retrofit costs: dependent on area, HVAC age, and insulation quality
        retrofit_multiplier = 5.0
        if insulation == 'Poor': retrofit_multiplier += 4.5
        if window == 'Single Pane': retrofit_multiplier += 3.0
        if hvac_age > 15: retrofit_multiplier += 5.0
        estimated_retrofit_cost = area * np.random.uniform(retrofit_multiplier * 0.8, retrofit_multiplier * 1.2)
        
        data.append({
            'building_id': b_id,
            'building_name': b_name,
            'building_type': b_type,
            'city': city,
            'state': state,
            'climate_zone': climate,
            'year_built': year_built,
            'floor_area_sqft': area,
            'number_of_floors': num_floors,
            'occupancy_count': occupancy,
            'energy_use_kwh': int(energy_use_kwh),
            'water_use_gallons': int(water_use_gallons),
            'electricity_cost': round(electricity_cost, 2),
            'gas_cost': round(gas_cost, 2),
            'maintenance_cost': round(maintenance_cost, 2),
            'carbon_emissions_kg': int(carbon_emissions_kg),
            'hvac_age': hvac_age,
            'insulation_quality': insulation,
            'window_type': window,
            'energy_star_score': energy_star,
            'last_retrofit_year': last_retrofit,
            'renewable_energy_pct': round(renewable_energy_pct, 1),
            'estimated_retrofit_cost': round(estimated_retrofit_cost, 2)
        })
        
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    return df

def check_is_building_dataset(df: pd.DataFrame) -> bool:
    """
    Checks if a DataFrame has the columns indicating it's a building performance dataset.
    """
    required_cols = {'building_id', 'building_name', 'building_type'}
    # Also support alternate mappings from previous project
    alt_cols = {'annual_energy_use_kbtu', 'annual_operating_cost', 'building_performance_risk_score'}
    
    cols = set(df.columns)
    return bool(required_cols.issubset(cols) or alt_cols.intersection(cols))

def load_building_data(uploaded_file=None, workspace_dir: str = ".") -> tuple[pd.DataFrame, str]:
    """
    Loads building data.
    - If uploaded_file is provided, tries to load it.
    - If not, checks for student_success_uci.csv in the workspace.
    - If student_success_uci.csv is present but is a student success dataset,
      or doesn't exist, it generates and loads data/sample_buildings.csv.
    """
    sample_path = os.path.join(workspace_dir, "data", "sample_buildings.csv")
    uci_path = os.path.join(workspace_dir, "student_success_uci.csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if check_is_building_dataset(df):
                return df, "Custom Building Dataset Uploaded"
            else:
                return None, "Error: Uploaded file does not match a building performance dataset schema."
        except Exception as e:
            return None, f"Error reading uploaded file: {str(e)}"
            
    # Check if student_success_uci.csv exists and is actually a building dataset
    if os.path.exists(uci_path):
        try:
            df = pd.read_csv(uci_path, sep=None, engine='python')
            if check_is_building_dataset(df):
                return df, "Using Existing Building Performance Dataset (student_success_uci.csv)"
            else:
                # File exists but is not building data (e.g. is the student success data)
                # Let's fallback to generating/loading sample_buildings.csv
                if os.path.exists(sample_path):
                    df_sample = pd.read_csv(sample_path)
                    return df_sample, "Loaded Synthetic Building Dataset (student_success_uci.csv detected as student data)"
                else:
                    df_sample = generate_synthetic_data(sample_path)
                    return df_sample, "Generated & Loaded Synthetic Building Dataset (student_success_uci.csv detected as student data)"
        except Exception as e:
            pass
            
    # If no UCI file or it failed, load/generate sample
    if os.path.exists(sample_path):
        try:
            df_sample = pd.read_csv(sample_path)
            return df_sample, "Loaded Synthetic Building Dataset"
        except Exception as e:
            df_sample = generate_synthetic_data(sample_path)
            return df_sample, f"Re-generated & Loaded Synthetic Building Dataset (loading sample failed: {str(e)})"
    else:
        df_sample = generate_synthetic_data(sample_path)
        return df_sample, "Generated & Loaded Synthetic Building Dataset"
