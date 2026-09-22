"""
Metrics and Business Analytics Aggregations for CDC Natality Data.

This module provides filtering logic and analytical computations for:
- Executive KPI calculations (totals, averages, peak states/months)
- Safe handling of edge cases (empty filters)
- Group-by aggregations for dashboard visualizations
"""

from typing import Any, Dict, List, Optional
import pandas as pd


def filter_dataset(
    df: pd.DataFrame,
    states: List[str],
    months: List[str],
    sex: str
) -> pd.DataFrame:
    """
    Applies user-selected filters to the natality dataset.
    Returns an empty DataFrame if states or months are unselected.
    """
    if not states or not months:
        return df.iloc[0:0].copy()

    mask = (df["State of Residence"].isin(states)) & (df["Month"].isin(months))

    if sex != "All":
        mask = mask & (df["Sex of Infant"] == sex)

    return df[mask].copy()


def calculate_kpis(filtered_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates the 5 required executive KPI metrics:
    1. Total births in the current selection
    2. Number of selected geographies
    3. Average births per selected month
    4. Geography with the highest selected birth count
    5. Month with the highest selected birth count

    Returns safe fallback values if the filtered DataFrame is empty.
    """
    if filtered_df.empty:
        return {
            "total_births": 0,
            "selected_geographies_count": 0,
            "avg_births_per_month": 0.0,
            "top_geography": "None",
            "top_geography_births": 0,
            "top_month": "None",
            "top_month_births": 0,
        }

    total_births = int(filtered_df["Births"].sum())
    unique_geos = int(filtered_df["State of Residence"].nunique())
    unique_months = int(filtered_df["Month"].nunique())

    # Average births per month across the active selection
    avg_per_month = total_births / unique_months if unique_months > 0 else 0.0

    # Geography with highest birth count
    geo_totals = (
        filtered_df.groupby("State of Residence")["Births"]
        .sum()
        .reset_index()
    )
    if not geo_totals.empty:
        top_geo_row = geo_totals.sort_values(by="Births", ascending=False).iloc[0]
        top_geo = str(top_geo_row["State of Residence"])
        top_geo_births = int(top_geo_row["Births"])
    else:
        top_geo = "None"
        top_geo_births = 0

    # Month with highest birth count
    month_totals = (
        filtered_df.groupby("Month", observed=True)["Births"]
        .sum()
        .reset_index()
    )
    if not month_totals.empty:
        top_month_row = month_totals.sort_values(by="Births", ascending=False).iloc[0]
        top_month = str(top_month_row["Month"])
        top_month_births = int(top_month_row["Births"])
    else:
        top_month = "None"
        top_month_births = 0

    return {
        "total_births": total_births,
        "selected_geographies_count": unique_geos,
        "avg_births_per_month": avg_per_month,
        "top_geography": top_geo,
        "top_geography_births": top_geo_births,
        "top_month": top_month,
        "top_month_births": top_month_births,
    }


def aggregate_by_month(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates birth counts by month in chronological sequence."""
    if filtered_df.empty:
        return pd.DataFrame(columns=["Month", "Births"])

    agg = (
        filtered_df.groupby("Month", observed=True)["Births"]
        .sum()
        .reset_index()
    )
    return agg


def aggregate_by_month_and_sex(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates birth counts by month and infant sex."""
    if filtered_df.empty:
        return pd.DataFrame(columns=["Month", "Sex of Infant", "Births"])

    agg = (
        filtered_df.groupby(["Month", "Sex of Infant"], observed=True)["Births"]
        .sum()
        .reset_index()
    )
    return agg


def aggregate_by_state(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates birth counts by state, sorted descending by volume."""
    if filtered_df.empty:
        return pd.DataFrame(columns=["State of Residence", "State Abbrev", "Births"])

    agg = (
        filtered_df.groupby(["State of Residence", "State Abbrev"])["Births"]
        .sum()
        .reset_index()
        .sort_values(by="Births", ascending=False)
    )
    return agg


def aggregate_state_by_month_matrix(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivots data into a 2D matrix (State rows x Month columns) for heatmap visualization.
    """
    if filtered_df.empty:
        return pd.DataFrame()

    pivot = filtered_df.pivot_table(
        index="State of Residence",
        columns="Month",
        values="Births",
        aggfunc="sum",
        fill_value=0,
        observed=True
    )
    return pivot
