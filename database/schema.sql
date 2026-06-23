-- EcoBuild Intelligence Database Schema

-- 1. Buildings Table
CREATE TABLE IF NOT EXISTS buildings (
    building_id TEXT PRIMARY KEY,
    building_name TEXT NOT NULL,
    building_type TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    climate_zone TEXT NOT NULL,
    year_built INTEGER NOT NULL,
    floor_area_sqft REAL NOT NULL,
    number_of_floors INTEGER NOT NULL,
    occupancy_count INTEGER NOT NULL,
    insulation_quality TEXT NOT NULL,
    window_type TEXT NOT NULL,
    last_retrofit_year INTEGER NOT NULL
);

-- 2. Monthly Energy Records Table
CREATE TABLE IF NOT EXISTS energy_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    electricity_kwh REAL NOT NULL,
    gas_kwh REAL NOT NULL,
    water_gallons REAL NOT NULL,
    electricity_cost REAL NOT NULL,
    gas_cost REAL NOT NULL,
    water_cost REAL NOT NULL,
    carbon_emissions_kg REAL NOT NULL,
    FOREIGN KEY (building_id) REFERENCES buildings (building_id) ON DELETE CASCADE
);

-- 3. Equipment Table
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id TEXT PRIMARY KEY,
    building_id TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    install_year INTEGER NOT NULL,
    condition TEXT NOT NULL,
    last_service_date TEXT NOT NULL,
    estimated_replacement_cost REAL NOT NULL,
    FOREIGN KEY (building_id) REFERENCES buildings (building_id) ON DELETE CASCADE
);

-- 4. Retrofit Recommendations Table
CREATE TABLE IF NOT EXISTS retrofit_recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id TEXT NOT NULL,
    recommendation_type TEXT NOT NULL,
    estimated_cost REAL NOT NULL,
    estimated_annual_savings REAL NOT NULL,
    estimated_carbon_reduction REAL NOT NULL,
    priority_score REAL NOT NULL,
    FOREIGN KEY (building_id) REFERENCES buildings (building_id) ON DELETE CASCADE
);

-- 5. AI Saved Reports Table
CREATE TABLE IF NOT EXISTS ai_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (building_id) REFERENCES buildings (building_id) ON DELETE CASCADE
);
