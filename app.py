"""
CDC Provisional Natality 2025 Streamlit Dashboard.

An educational business analytics dashboard designed to explore geographic,
seasonal, and sex-based variations in provisional 2025 U.S. birth counts.
"""

from typing import List
import pandas as pd
import streamlit as st

from src.charts import (
    plot_monthly_sex_comparison,
    plot_monthly_trend,
    plot_sex_donut,
    plot_state_month_heatmap,
    plot_state_ranking,
    plot_top_bottom_states,
    plot_us_choropleth,
)
from src.data_loader import MONTH_ORDER, load_natality_data
from src.metrics import (
    aggregate_by_month,
    aggregate_by_month_and_sex,
    aggregate_by_state,
    aggregate_state_by_month_matrix,
    calculate_kpis,
    filter_dataset,
)

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CDC Provisional Natality 2025",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom light styling to reinforce clean typography and contrast
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-label {
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-subtext {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 2px;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-primary { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; }
    .badge-warning { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. Data Loading & Session State Initialization
# -----------------------------------------------------------------------------
try:
    df_raw = load_natality_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

all_states: List[str] = sorted(df_raw["State of Residence"].unique().tolist())
all_months: List[str] = [m for m in MONTH_ORDER if m in df_raw["Month"].unique()]
sex_options: List[str] = ["All", "Female", "Male"]

# Initialize default widget states
if "filter_states" not in st.session_state:
    st.session_state.filter_states = all_states
if "filter_months" not in st.session_state:
    st.session_state.filter_months = all_months
if "filter_sex" not in st.session_state:
    st.session_state.filter_sex = "All"


def reset_filters() -> None:
    """Callback to reset all sidebar filters back to full dataset defaults."""
    st.session_state.filter_states = all_states
    st.session_state.filter_months = all_months
    st.session_state.filter_sex = "All"


def select_all_states() -> None:
    """Callback to select all 51 geographies."""
    st.session_state.filter_states = all_states


def select_all_months() -> None:
    """Callback to select all 12 calendar months."""
    st.session_state.filter_months = all_months


# -----------------------------------------------------------------------------
# 3. Sidebar Controls
# -----------------------------------------------------------------------------
st.sidebar.title("🎛️ Dashboard Filters")
st.sidebar.markdown(
    "Filter the provisional birth observations across geographic, temporal, and demographic dimensions."
)

# Action Buttons: Select All & Reset
btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    if st.button("🔄 Reset Filters", use_container_width=True, on_click=reset_filters):
        st.rerun()
with btn_col2:
    if st.button("🌐 All States", use_container_width=True, on_click=select_all_states):
        st.rerun()

# State Multiselect
selected_states = st.sidebar.multiselect(
    "Geographies (States & D.C.)",
    options=all_states,
    key="filter_states",
    help="Select one or more of the 50 U.S. states and District of Columbia.",
)

# Month Multiselect
if st.sidebar.button("📅 Select All Months", use_container_width=True, on_click=select_all_months):
    st.rerun()

selected_months = st.sidebar.multiselect(
    "Months (Chronological)",
    options=all_months,
    key="filter_months",
    help="Filter by calendar months (January through December).",
)

# Infant-Sex Selector
selected_sex = st.sidebar.radio(
    "Infant Sex Category",
    options=sex_options,
    key="filter_sex",
    help="Select 'All' to view combined counts, or filter by a specific sex.",
)

# Active Filter Summary
st.sidebar.markdown("---")
st.sidebar.subheader("Active Filter Summary")
st.sidebar.markdown(
    f"""
    - **Geographies:** `{len(selected_states)}` of `{len(all_states)}` selected
    - **Months:** `{len(selected_months)}` of `{len(all_months)}` selected
    - **Infant Sex:** `{selected_sex}`
    """
)
st.sidebar.caption("Source: CDC WONDER Provisional Natality Statistics (2025)")


# -----------------------------------------------------------------------------
# 4. Header & Educational Notices
# -----------------------------------------------------------------------------
st.title("👶 CDC Provisional Natality Dashboard (2025)")
st.markdown(
    "**An interactive exploration of geographic, seasonal, and sex-based birth counts across the United States.**"
)

# Educational Disclaimer & Provisional Data Notice (Rule 5, 6, 7, 9)
with st.container():
    st.info(
        """
        ℹ️ **Important Analytical Notes for Business Analytics Students:**
        1. **Births are Event Counts, Not Rates:** Figures represent raw birth counts, not crude birth rates or fertility rates. Variations between states primarily reflect total population scale. Comparing California to Wyoming illustrates volume differences, not per-capita fertility.
        2. **Provisional Data:** Data reflect preliminary 2025 counts from the CDC National Center for Health Statistics (NCHS) and are subject to late-reporting revisions.
        3. **Balanced Dataset:** The dataset contains complete reporting across all 51 geographies, 12 calendar months, and 2 infant-sex categories ($51 \\times 12 \\times 2 = 1,224$ records).
        """
    )


# -----------------------------------------------------------------------------
# 5. Data Filtering & Defensive Check
# -----------------------------------------------------------------------------
df_filtered = filter_dataset(df_raw, selected_states, selected_months, selected_sex)

if df_filtered.empty:
    st.warning(
        """
        ⚠️ **No observations match your current filter selection.**
        
        Please select at least one geography and one month in the sidebar, or click the **Reset Filters** button above.
        """
    )
    st.stop()


# -----------------------------------------------------------------------------
# 6. Executive KPI Cards
# -----------------------------------------------------------------------------
kpis = calculate_kpis(df_filtered)

kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Births</div>
            <div class="metric-value">{kpis['total_births']:,}</div>
            <div class="metric-subtext">Cumulative in selection</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[1]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Selected Geographies</div>
            <div class="metric-value">{kpis['selected_geographies_count']} <span style="font-size:16px;color:#94A3B8;">/ 51</span></div>
            <div class="metric-subtext">States & D.C.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[2]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Monthly Average</div>
            <div class="metric-value">{kpis['avg_births_per_month']:,.0f}</div>
            <div class="metric-subtext">Births per selected month</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[3]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Top Geography</div>
            <div class="metric-value" style="font-size: 20px;">{kpis['top_geography']}</div>
            <div class="metric-subtext">{kpis['top_geography_births']:,} births</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[4]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Peak Month</div>
            <div class="metric-value" style="font-size: 20px;">{kpis['top_month']}</div>
            <div class="metric-subtext">{kpis['top_month_births']:,} births</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")  # Spacing


# -----------------------------------------------------------------------------
# 7. Dashboard Tabs
# -----------------------------------------------------------------------------
tab_overview, tab_geo, tab_monthly_sex, tab_table, tab_about = st.tabs(
    [
        "📈 Overview",
        "🗺️ Geographic Analysis",
        "📅 Monthly & Sex Analysis",
        "📋 Data Table & Download",
        "📖 About the Data",
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Executive Overview")
    st.markdown(
        "A macro-level view of 2025 birth delivery volumes across calendar months and demographic categories."
    )

    row1_col1, row1_col2 = st.columns([3, 2])
    with row1_col1:
        df_month_agg = aggregate_by_month(df_filtered)
        fig_trend = plot_monthly_trend(df_month_agg)
        st.plotly_chart(fig_trend, use_container_width=True)

    with row1_col2:
        fig_donut = plot_sex_donut(df_filtered)
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")
    st.subheader("Geographic Extremes: High vs. Low Volume States")
    st.markdown(
        "Direct comparison of the top 5 highest-volume delivery states and bottom 5 states in the active selection."
    )
    df_state_agg = aggregate_by_state(df_filtered)
    fig_top_bottom = plot_top_bottom_states(df_state_agg, n=5)
    st.plotly_chart(fig_top_bottom, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 2: GEOGRAPHIC ANALYSIS
# -----------------------------------------------------------------------------
with tab_geo:
    st.subheader("Geographic Distribution Across U.S. States")
    st.markdown(
        "Explore how birth volumes vary geographically. Note that absolute volume strongly correlates with state population."
    )

    df_state_agg = aggregate_by_state(df_filtered)

    # Choropleth Map
    fig_map = plot_us_choropleth(df_state_agg)
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    geo_col1, geo_col2 = st.columns([1, 1])

    with geo_col1:
        st.subheader("State Volume Ranking")
        st.caption("All selected states ranked from highest to lowest cumulative births.")
        fig_ranking = plot_state_ranking(df_state_agg)
        st.plotly_chart(fig_ranking, use_container_width=True)

    with geo_col2:
        st.subheader("State-by-Month Heatmap Matrix")
        st.caption("Matrix showing birth volume intensity across states and calendar months.")
        df_matrix = aggregate_state_by_month_matrix(df_filtered)
        if not df_matrix.empty:
            fig_heatmap = plot_state_month_heatmap(df_matrix)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Insufficient data to construct state-by-month matrix.")


# -----------------------------------------------------------------------------
# TAB 3: MONTHLY & SEX ANALYSIS
# -----------------------------------------------------------------------------
with tab_monthly_sex:
    st.subheader("Seasonal Trends & Sex Disaggregation")
    st.markdown(
        "Detailed comparison of male and female births over the course of the 2025 calendar year."
    )

    df_month_sex = aggregate_by_month_and_sex(df_filtered)
    fig_month_sex = plot_monthly_sex_comparison(df_month_sex)
    st.plotly_chart(fig_month_sex, use_container_width=True)

    st.markdown("---")
    st.subheader("Analytical Insights: Natural Sex Ratios")
    st.markdown(
        """
        In human populations, the biological **secondary sex ratio at birth** typically ranges between 
        **103 to 106 male births per 100 female births** (approximately ~51.2% male and 48.8% female).
        
        Using the table below, students can observe how consistently this biological ratio holds true 
        across every month in the 2025 provisional dataset.
        """
    )

    # Pivot sex breakdown by month for student inspection
    if not df_month_sex.empty:
        pivot_sex = df_month_sex.pivot(index="Month", columns="Sex of Infant", values="Births")
        if "Female" in pivot_sex.columns and "Male" in pivot_sex.columns:
            pivot_sex["Total"] = pivot_sex["Female"] + pivot_sex["Male"]
            pivot_sex["Female %"] = (pivot_sex["Female"] / pivot_sex["Total"] * 100).round(2)
            pivot_sex["Male %"] = (pivot_sex["Male"] / pivot_sex["Total"] * 100).round(2)
            pivot_sex["Sex Ratio (M per 100 F)"] = (
                (pivot_sex["Male"] / pivot_sex["Female"]) * 100
            ).round(1)

            st.dataframe(
                pivot_sex.style.format(
                    {
                        "Female": "{:,.0f}",
                        "Male": "{:,.0f}",
                        "Total": "{:,.0f}",
                        "Female %": "{:.2f}%",
                        "Male %": "{:.2f}%",
                        "Sex Ratio (M per 100 F)": "{:.1f}",
                    }
                ),
                use_container_width=True,
            )


# -----------------------------------------------------------------------------
# TAB 4: DATA TABLE & DOWNLOAD
# -----------------------------------------------------------------------------
with tab_table:
    st.subheader("Filtered Dataset & Data Export")
    st.markdown(
        "Examine the underlying observation-level data or download the current filtered view for spreadsheet modeling."
    )

    # Display record count
    st.write(f"Displaying **{len(df_filtered):,}** observations matching active filters:")

    # Searchable & sortable table
    st.dataframe(
        df_filtered[["State of Residence", "State Abbrev", "Month", "Month Code", "Year Code", "Sex of Infant", "Births"]],
        column_config={
            "Births": st.column_config.NumberColumn(
                "Births",
                format="%d",
                help="Provisional birth count for this state, month, and sex.",
            ),
            "Month Code": st.column_config.NumberColumn(
                "Month Code",
                format="%d",
            ),
            "Year Code": st.column_config.NumberColumn(
                "Year",
                format="%d",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    # CSV Download Button
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="cdc_provisional_births_filtered_2025.csv",
        mime="text/csv",
        help="Click to export the currently filtered observations to a standard CSV file.",
    )

    st.markdown("---")
    st.subheader("Summary Descriptive Statistics")
    st.markdown(
        "Basic distribution statistics for the `Births` variable in the active selection."
    )
    desc = df_filtered["Births"].describe().to_frame().T
    desc.columns = ["Count", "Mean", "Std Dev", "Min", "25%", "Median", "75%", "Max"]
    st.dataframe(
        desc.style.format(
            {
                "Count": "{:,.0f}",
                "Mean": "{:,.2f}",
                "Std Dev": "{:,.2f}",
                "Min": "{:,.0f}",
                "25%": "{:,.0f}",
                "Median": "{:,.0f}",
                "75%": "{:,.0f}",
                "Max": "{:,.0f}",
            }
        ),
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# TAB 5: ABOUT THE DATA
# -----------------------------------------------------------------------------
with tab_about:
    st.subheader("About the CDC Provisional Natality Dataset")
    st.markdown(
        """
        ### 1. Data Provenance & Source
        - **Source:** Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS).
        - **System:** CDC WONDER (Wide-ranging ONline Data for Epidemiologic Research) Provisional Natality Database.
        - **Temporal Scope:** Calendar year 2025 (all 12 months).
        - **Status:** **Provisional**. Final vital statistics releases may contain minor adjustments due to delayed registration of birth certificates.
        
        ---
        
        ### 2. Data Dictionary
        
        | Variable Name | Type | Description | Values / Range |
        | :--- | :--- | :--- | :--- |
        | **`State of Residence`** | Text | U.S. State or territory of maternal residence | 50 U.S. States + District of Columbia |
        | **`State Abbrev`** | Text | Standard 2-letter USPS postal code | `AL`, `AK`, ..., `WY` |
        | **`Month`** | Categorical | Calendar month name of birth occurrence | `January` through `December` |
        | **`Month Code`** | Integer | Chronological sequence integer for calendar month | `1` to `12` |
        | **`Year Code`** | Integer | Reporting calendar year | `2025` |
        | **`Sex of Infant`** | Text | Biological sex of newborn child | `'Female'`, `'Male'` |
        | **`Births`** | Integer | Aggregate number of live births recorded in this cell | `177` to `17,627` |
        
        ---
        
        ### 3. Key Business Analytics Lessons
        
        #### Lesson A: The Difference Between Event Counts and Rates
        A common pitfall in business analytics is confusing **activity volume** (counts) with **incidence propensity** (rates).
        - A count tells you *how many* events occurred.
        - A rate tells you *how frequently* events occurred relative to an exposed population.
        
        In this dashboard, **California** has approximately $391,248$ births while **Vermont** has approximately $4,586$ births. 
        Does California have an "unusually high birth rate"? Not necessarily—California simply has approximately 39 million residents, 
        whereas Vermont has roughly 650,000 residents. Without an external census population table, calculating a crude birth rate 
        (e.g., $\\frac{\\text{Births}}{\\text{Total Population}} \\times 1,000$) or general fertility rate is analytically impermissible.
        
        #### Lesson B: Working with Balanced Panel Data
        In econometrics and business analytics, a **balanced panel** occurs when every cross-sectional unit (51 states) is observed 
        for every time interval (12 months) and demographic subgroup (2 sexes).
        $$\\text{Total Observations} = 51 \\times 12 \\times 2 = 1,224$$
        Because this panel is fully balanced, aggregations across any dimension are consistent and require no imputation for missing cells.
        
        #### Lesson C: Data Privacy and Suppression Thresholds
        Federal public health reporting requires protecting individual privacy. The CDC WONDER system typically masks or suppresses 
        cell values smaller than 10 (replacing them with `*` or `Unreliable`). Because this dataset is aggregated at the state level, 
        even the smallest monthly cell (Vermont females in February) reached 177 births—well above the suppression threshold.
        """
    )
