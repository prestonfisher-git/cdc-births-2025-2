# CDC Provisional Natality 2025 Streamlit Dashboard

An interactive, educational business analytics dashboard designed for undergraduate students to explore geographic, seasonal, and sex-based variations in provisional 2025 U.S. birth counts.

---

## 📚 Pedagogical Objectives

1. **Count vs. Rate Distinction:** Understand why raw event counts (births) must not be confused with incidence rates (crude birth rate, general fertility rate) without external population denominators.
2. **Balanced Panel Data:** Explore an econometric panel dataset with complete observations across 51 geographies, 12 months, and 2 infant sexes ($51 \times 12 \times 2 = 1,224$ records).
3. **Biological Sex Ratios:** Observe empirical confirmation of the secondary sex ratio at birth (~103–106 males per 100 females) across calendar months.
4. **Data Visualization Best Practices:** Learn how to design dashboards with zero-baselines on bar charts, accessible high-contrast palettes, responsive layouts, and defensive empty-state handling.

---

## 🛠️ Project Structure

```
cdc-births-2025-2/
├── app.py                         # Streamlit UI, filters, KPIs, and 5-tab layout
├── requirements.txt               # Project dependencies
├── README.md                      # Student guide and documentation
├── data/
│   └── Provisional_Natality_2025_CDC.xlsx  # Read-only CDC source workbook
└── src/
    ├── __init__.py
    ├── data_loader.py             # Cached loading (@st.cache_data), validation, USPS codes
    ├── metrics.py                 # Filter logic, KPI formulas, and aggregation helpers
    └── charts.py                  # Plotly charts (trends, maps, bars, heatmaps)
```

---

## 🚀 Running the Dashboard Locally

1. **Activate your Python environment** (Python 3.10+ recommended).
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```
4. The dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## 📊 Dashboard Modules

1. **Executive KPI Cards:**
   - Total Births in selection
   - Active Geographies count
   - Monthly Average births
   - Highest-Volume Geography
   - Peak Calendar Month
2. **Overview Tab:**
   - Chronological monthly trajectory (January to December)
   - Female vs. Male distribution donut chart
   - Top 5 vs. Bottom 5 states comparison
3. **Geographic Analysis Tab:**
   - Interactive U.S. Choropleth Map with state abbreviations
   - Complete state volume ranking (zero-baseline enforced)
   - State-by-Month seasonal birth heatmap matrix
4. **Monthly & Sex Analysis Tab:**
   - Side-by-side grouped bars for female vs. male births
   - Monthly natural sex ratio table (Males per 100 Females)
5. **Data Table & Download Tab:**
   - Searchable and sortable filtered table
   - Instant CSV export of filtered data
   - Descriptive summary statistics
6. **About the Data Tab:**
   - Full data dictionary
   - CDC WONDER source attribution and provisional status explanation
   - In-depth business analytics lessons on vital statistics

---

## 🛡️ Data Quality & Verification

- **Total Observations:** 1,224
- **Unique Geographies:** 51 (50 States + District of Columbia)
- **Unique Months:** 12 (January to December)
- **Infant Sexes:** 2 (`Female`, `Male`)
- **Missing Values:** 0
- **Duplicate Rows:** 0
- **Cumulative Birth Count:** 3,604,640
