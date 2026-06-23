import sqlite3
import os
import pandas as pd
import numpy as np
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecobuild.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force=False):
    """
    Initializes the SQLite database tables using schema.sql.
    """
    if force and os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Error removing database: {e}")
            
    conn = get_db_connection()
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
        
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()

def is_db_seeded() -> bool:
    """
    Checks if the database has already been seeded with building records.
    """
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM buildings")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False

def seed_db_from_dataframe(df: pd.DataFrame):
    """
    Seeds the SQLite database using a fully metrics-calculated building DataFrame.
    """
    init_db(force=True) # Reset database to seed fresh
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_year = 2026
    
    for _, row in df.iterrows():
        b_id = row['building_id']
        
        # 1. Insert into buildings table
        cursor.execute("""
            INSERT OR REPLACE INTO buildings (
                building_id, building_name, building_type, city, state, climate_zone,
                year_built, floor_area_sqft, number_of_floors, occupancy_count,
                insulation_quality, window_type, last_retrofit_year
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b_id, row['building_name'], row['building_type'], row['city'], row['state'], row['climate_zone'],
            int(row['year_built']), float(row['floor_area_sqft']), int(row['number_of_floors']), int(row['occupancy_count']),
            row['insulation_quality'], row['window_type'], int(row['last_retrofit_year'])
        ))
        
        # 2. Seed monthly energy records for Year 2025 (12 months)
        # Apply seasonal scaling based on climate zone
        climate = row['climate_zone']
        
        avg_elec_kwh = (row['energy_use_kwh'] * 0.70) / 12.0
        avg_gas_kwh = (row['energy_use_kwh'] * 0.30) / 12.0
        avg_water_gal = row['water_use_gallons'] / 12.0
        
        avg_elec_cost = row['electricity_cost'] / 12.0
        avg_gas_cost = row['gas_cost'] / 12.0
        avg_water_cost = (row['water_use_gallons'] * 0.008) / 12.0
        avg_carbon = row['carbon_emissions_kg'] / 12.0
        
        for m in range(1, 13):
            # Define seasonal factor multipliers
            elec_multiplier = 1.0
            gas_multiplier = 1.0
            
            if 'Cold' in climate:
                # Winter gas spike (heating), summer electricity spike (cooling)
                if m in [12, 1, 2]: # Winter
                    gas_multiplier = 1.7
                    elec_multiplier = 0.7
                elif m in [6, 7, 8]: # Summer
                    gas_multiplier = 0.3
                    elec_multiplier = 1.5
                else: # Shoulder
                    gas_multiplier = 0.8
                    elec_multiplier = 0.9
            elif 'Hot' in climate:
                # Summer electricity spike (heavy AC)
                if m in [6, 7, 8, 9]:
                    elec_multiplier = 1.8
                    gas_multiplier = 0.4
                elif m in [12, 1, 2]:
                    elec_multiplier = 0.6
                    gas_multiplier = 1.4
                else:
                    elec_multiplier = 1.0
                    gas_multiplier = 0.8
            else: # Marine / Mild / Mixed
                if m in [7, 8]:
                    elec_multiplier = 1.3
                    gas_multiplier = 0.5
                elif m in [12, 1]:
                    elec_multiplier = 0.8
                    gas_multiplier = 1.4
                    
            # Add small random noise (+/- 5%)
            noise = np.random.uniform(0.95, 1.05)
            
            m_elec_kwh = avg_elec_kwh * elec_multiplier * noise
            m_gas_kwh = avg_gas_kwh * gas_multiplier * noise
            m_water_gal = avg_water_gal * noise
            
            m_elec_cost = avg_elec_cost * elec_multiplier * noise
            m_gas_cost = avg_gas_cost * gas_multiplier * noise
            m_water_cost = avg_water_cost * noise
            m_carbon = avg_carbon * ((elec_multiplier * 0.7 + gas_multiplier * 0.3)) * noise
            
            cursor.execute("""
                INSERT INTO energy_records (
                    building_id, year, month, electricity_kwh, gas_kwh, water_gallons,
                    electricity_cost, gas_cost, water_cost, carbon_emissions_kg
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                b_id, 2025, m, float(m_elec_kwh), float(m_gas_kwh), float(m_water_gal),
                float(m_elec_cost), float(m_gas_cost), float(m_water_cost), float(m_carbon)
            ))
            
        # 3. Seed equipment details
        # HVAC System
        hvac_install = current_year - int(row['hvac_age'])
        hvac_cond = 'Good'
        if row['hvac_age'] > 15: hvac_cond = 'Poor'
        elif row['hvac_age'] > 8: hvac_cond = 'Fair'
        elif row['hvac_age'] <= 3: hvac_cond = 'Excellent'
        
        hvac_replacement = row['floor_area_sqft'] * np.random.uniform(3.5, 6.0)
        
        cursor.execute("""
            INSERT OR REPLACE INTO equipment (
                equipment_id, building_id, equipment_type, install_year, condition,
                last_service_date, estimated_replacement_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"EQ-HVAC-{b_id}", b_id, 'HVAC System', hvac_install, hvac_cond,
            f"{current_year - 1}-08-15", float(hvac_replacement)
        ))
        
        # Windows
        win_cond = 'Fair'
        if row['window_type'] == 'Triple Pane': win_cond = 'Excellent'
        elif row['window_type'] == 'Single Pane': win_cond = 'Poor'
        win_replacement = row['floor_area_sqft'] * np.random.uniform(1.5, 3.0)
        
        cursor.execute("""
            INSERT OR REPLACE INTO equipment (
                equipment_id, building_id, equipment_type, install_year, condition,
                last_service_date, estimated_replacement_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"EQ-WIN-{b_id}", b_id, 'Window Glazing', int(row['year_built']), win_cond,
            "N/A", float(win_replacement)
        ))
        
        # 4. Seed Retrofit recommendations
        risk_cat = row['building_performance_risk_category']
        rec_type = 'None'
        if risk_cat in ['High', 'Critical']:
            rec_type = 'HVAC Heat Pump Upgrade & Smart Controls'
            cost = row['estimated_retrofit_cost'] * 0.6
            savings = row['estimated_cost_savings'] * 0.6
            carbon = row['estimated_carbon_reduction_kg'] * 0.6
        elif risk_cat == 'Medium':
            rec_type = 'Insulation Upgrade & LED Retrofit'
            cost = row['estimated_retrofit_cost'] * 0.4
            savings = row['estimated_cost_savings'] * 0.4
            carbon = row['estimated_carbon_reduction_kg'] * 0.4
        else:
            rec_type = 'Smart Thermostat & Commissioning'
            cost = row['estimated_retrofit_cost'] * 0.1
            savings = row['estimated_cost_savings'] * 0.1
            carbon = row['estimated_carbon_reduction_kg'] * 0.1
            
        cursor.execute("""
            INSERT OR REPLACE INTO retrofit_recommendations (
                building_id, recommendation_type, estimated_cost,
                estimated_annual_savings, estimated_carbon_reduction, priority_score
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            b_id, rec_type, float(cost), float(savings), float(carbon), float(row['retrofit_priority_score'])
        ))
        
    conn.commit()
    conn.close()

def query_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    """
    Executes a SELECT query on the SQLite database and returns a Pandas DataFrame.
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_write(query: str, params: tuple = ()):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()
