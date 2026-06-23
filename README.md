# EcoBuild Intelligence: Building Energy, Cost, Carbon, and Retrofit Analytics Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey.svg?style=flat&logo=sqlite&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-brightgreen.svg?style=flat&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)

---

## Project Overview
Educational institutions, commercial enterprises, and real estate investment trusts (REITs) face significant challenges in managing utility expenses, carbon footprints, and building maintenance. This project provides a complete, multi-layered data analytics platform that identifies high-cost, high-emission buildings, and pinpoints operational risks (e.g., aging HVAC systems, poor envelope insulation, inefficient window glazing). By combining standard building operations data with predictive retrofit modeling, this project demonstrates a comprehensive approach to building performance engineering and ESG (Environmental, Social, and Governance) analytics.

## Portfolio Highlights
This project demonstrates proficiency in:
*   **SQL Querying**: Complex relational schemas, table joins, and monthly utility KPI extraction.
*   **Python Data Incleaning**: Handling missing inputs, column schema mapping, and derived metrics engineering with Pandas and NumPy.
*   **Exploratory Data Analysis (EDA)**: Visualizing energy and emission distributions, correlation profiles, and building benchmarking patterns.
*   **KPI Design**: Defining and calculating critical engineering indicators like Energy Use Intensity (EUI), Carbon Intensity, and Energy Cost Ratios.
*   **Multi-Factor Scoring Models**: Structuring building performance risk (0-100) and retrofit prioritization scores to guide capital allocation.
*   **Dual In-App Reporting Engines**: Building a query processor integrating OpenAI API key check with local rule-based fallback handlers to respond to natural language portfolio queries.
*   **Synthetic Data Generation**: Simulating realistic multi-property operations and monthly utility billing profiles with seasonal variations.

---

## Business Problem
High building utility bills and carbon footprints lead to financial inefficiency and failure to meet ESG compliance mandates. Real estate and sustainability managers struggle to analyze their portfolios because data is trapped across disjointed billing systems, manual spreadsheets, and physical hardware records. Portfolio managers need a way to quickly identify poorly performing properties, prioritize retrofit investments, and predict return-on-investment (ROI) before dedicating capital.

## Project Objective
To build a multi-layered data analytics solution that:
1.  **Ingests & Validates** building datasets, standardizing field names from arbitrary formats or public datasets (like NYC LL84 or Seattle building benchmarking data).
2.  **Identifies At-Risk Assets** using a multi-factor risk scoring system (combining HVAC age, insulation quality, glazing efficiency, EUI, and costs).
3.  **Prioritizes Retrofit Pipelines** based on capital payback years, energy reductions, and cost savings.
4.  **Generates AI-Assisted or Rule-Based Executive Reports** to summarize single buildings and monthly portfolio KPI progression.

---

## Dataset Description
*   **Benchmarking Ingestion (Mode 1)**: Supports direct upload of real-world public benchmarking datasets (e.g., NYC LL84, Seattle energy benchmarking) or previous analytics schemas, standardizing headers, converting $kBTU$ values, and filling missing bounds.
*   **Default Synthetic Dataset (Mode 2)**: Programmatically simulates a realistic portfolio of **2,500 buildings** inside `data/sample_buildings.csv` detailing:
    *   *Metadata*: Type (Office, Lab, Hospital, School, etc.), area ($sqft$), floors, and climate zone.
    *   *Building Envelope*: Insulation quality (Poor, Fair, Good, Excellent) and windows (Single, Double, Triple Pane).
    *   *Equipment Inventory*: HVAC system age and condition profiles.
    *   *Utility Costs*: Annual electricity, gas, and water costs.

> [!IMPORTANT]
> This platform implements a validation step. If an uploaded file does not match a building benchmarking structure (for example, if `student_success_uci.csv` is loaded), the app flags the schema issue, issues a notification in the sidebar, and automatically loads the default synthetic dataset to prevent application failure.

---

## Tools and Technologies
*   **Python**: Data processing (Pandas, NumPy) and user interface (Streamlit).
*   **Plotly Express**: Interactive web charts and data visualizations.
*   **SQL (SQLite)**: Relational database storing assets, monthly billing, and audit summaries.
*   **OpenAI API**: Narrative generation for audit summaries (with rule-based fallback).
*   **python-dotenv**: Environment configuration key storage.

---

## Folder Structure
```
ecobuild-intelligence/
├── data/
│   ├── sample_buildings.csv             # Generated 2,500 building record dataset
│   └── building_performance_dashboard_data.csv
├── pages/                               # Multi-page dashboard layouts
│   ├── 1_Portfolio_Overview.py
│   ├── 2_Building_Comparison.py
│   ├── 3_Risk_Analysis.py
│   ├── 4_Retrofit_Prioritization.py
│   ├── 5_Carbon_Sustainability.py
│   ├── 6_Building_Profile.py
│   └── 7_AI_Assistant.py
├── src/                                 # Platform source logic
│   ├── data_loader.py                   # Data Ingestion & Synthetic Generator
│   ├── data_cleaning.py                 # Column renaming & mapping
│   ├── metrics.py                       # Derived performance metrics
│   ├── risk_scoring.py                  # Multi-factor risk calculation
│   ├── retrofit.py                      # Payback & priority calculations
│   ├── ai_reports.py                    # OpenAI & rule-based assistants
│   └── database.py                      # SQLite DDL initializer and seeder
├── database/
│   ├── schema.sql                       # SQLite relational schema
│   └── ecobuild.db                      # Local seeded SQLite instance
├── reports/
│   └── sample_monthly_report.md         # Sample audit summary
├── visuals/
│   └── dashboard_screenshots_placeholder.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Methodology
1.  **Data Generation & Cleaning**: Used Python to simulate buildings, mechanical ages, and energy rates. Cleaned and normalized columns, ensuring EUI values and Energy Star scores were within valid boundaries.
2.  **Relational Database Mapping**: Populated SQLite tables representing static attributes, monthly utility details (injecting seasonal summer cooling and winter heating variations based on climate zone), and mechanical equipment conditions.
3.  **Risk & Retrofit Priority Modeling**: Formulated risk scores (0-100) and retrofit prioritization scores (0-100) based on weighted factors (EUI, emissions, cost, insulation, HVAC, glazing).
4.  **Executive Auditing**: Implemented a query assistant that translates questions into dataset metrics, providing detailed analysis reports.

---

## Key Analysis Questions
*   Which properties have the highest energy waste intensity (EUI) relative to their peers?
*   How does the age of HVAC equipment directly impact energy consumption and maintenance risks?
*   Which building types are responsible for the largest absolute greenhouse gas emissions?
*   Which properties should receive capital retrofit funding first to maximize cost savings and emissions reduction?

---

## Key KPIs
*   **Energy Use Intensity (EUI)**: Annual energy consumed per square foot ($kWh/sqft$).
*   **Operating Cost per Sqft**: Annual utility and maintenance cost divided by area ($/sqft$).
*   **Carbon Intensity**: Annual carbon footprint per square foot ($kg\text{ }CO_2e/sqft$).
*   **Risk Score (0-100)**: Multi-attribute operational health classification.
*   **Retrofit Priority (0-100)**: Weighted priority rank representing investment return.
*   **Simple Payback (Years)**: Estimated retrofit cost divided by projected annual utility savings.

---

## Visual Insights
Below are key visualizations generated inside the dashboard:

1.  **Portfolio Energy & Carbon Consumption by Property Type**  
    Bar charts identifying high-intensity segments (e.g., hospitals and labs) vs. low-intensity properties (e.g., schools and residential).
2.  **Asset Benchmarking Scatter Plot**  
    Interactive bubble charts correlating floor area vs. annual energy use, color-coded by risk category to isolate outliers.
3.  **Operational Risk & Age Distributions**  
    Risk histograms and age vs. risk correlation curves mapping legacy assets.
4.  **Retrofit Payback Schedules**  
    Payback period charts indicating timelines across Low, Medium, High, and Critical investment tiers.
5.  **Monthly Seasonal Trends**  
    Stacked utility cost bars detailing monthly electricity, gas, and water costs.

---

## Main Insights & Recommendations
*   **Insight**: Buildings with HVAC systems older than 15 years and poor insulation operate at an average of **28% higher EUI** than peers.
    *   *Recommendation*: Allocate immediate CAPEX to the top 5 high-priority candidates identified in the priority list to execute HVAC conversions and envelope weatherization.
*   **Insight**: Transitioning critical-risk properties to energy efficiency upgrades generates an average **18% - 25% utility bill reduction**, yielding a portfolio-wide cost savings of over **$75M annually**.
    *   *Recommendation*: Implement utility incentive auditing and leverage federal tax credits to offset the initial upgrade costs, reducing the weighted payback period below 5 years.

---

## How to Run the Project

### Prerequisites
*   Python 3.9+
*   Git

### Installation
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SharadhaKarthikeyan/ecobuild-intelligence.git
    ```
2.  **Navigate to the project folder**:
    ```bash
    cd ecobuild-intelligence
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Platform
1.  Set up environment variables (optional for OpenAI integration):
    ```bash
    cp .env.example .env
    # Add your OPENAI_API_KEY inside the .env file if available
    ```
2.  Launch the Streamlit dashboard:
    ```bash
    streamlit run app.py
    ```

### Using SQL Database Integration
The database files are managed in `database/`. You can connect to `ecobuild.db` using any SQLite viewer to query tables:
*   `buildings`: Static property features.
*   `energy_records`: Monthly historical consumption.
*   `equipment`: HVAC/Glazing details.
*   `retrofit_recommendations`: Upgrade costs and priorities.
*   `ai_reports`: Logged performance audit summaries.

---

## Project Limitations
*   **Static Calculations**: Risk weights and retrofit savings are based on typical building engineering benchmarks rather than dynamic, hourly thermodynamic modeling.
*   **Simplified Rates**: Utility rates are represented as static annual averages, ignoring complex time-of-use demand charges.

## Future Improvements
*   **Predictive ML Modeling**: Train regression models (e.g. Random Forests) on ASHRAE building audits to predict energy savings based on real-world inputs.
*   **Live Utility API Ingestion**: Integrate with the EPA ENERGY STAR Portfolio Manager API to automate monthly billing imports.

---
**Author: Sharadha Karthikeyan**
