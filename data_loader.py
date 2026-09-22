"""
Data Loader and Validation Module for CDC Provisional Natality 2025.

This module is designed for business analytics students to understand:
1. How to load Excel workbooks efficiently using caching (st.cache_data).
2. How to validate data integrity defensively before dashboard rendering.
3. How to map geographic entities to standard postal codes for spatial mapping.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

# Ordered list of calendar months to preserve chronological sequence
MONTH_ORDER: List[str] = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Standard 2-letter postal abbreviations for all 50 US States + District of Columbia
STATE_TO_ABBREV: Dict[str, str] = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def get_data_path() -> Path:
    """
    Returns the resolved path to the Excel file.
    Uses pathlib to ensure cross-platform compatibility across Windows,
    macOS, Linux, and Streamlit Community Cloud.
    """
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "data" / "Provisional_Natality_2025_CDC.xlsx"


def validate_dataset(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Performs data quality checks against expected vital statistics benchmarks:
    - 1,224 observations (51 states * 12 months * 2 sexes)
    - 6 expected columns
    - 0 missing values
    - 0 duplicate rows
    - Expected total birth count: 3,604,640
    """
    issues = []
    expected_cols = [
        "State of Residence", "Month", "Month Code",
        "Year Code", "Sex of Infant", "Births"
    ]
    
    # 1. Column verification
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")
        
    # 2. Row count verification
    if len(df) != 1224:
        issues.append(f"Expected 1,224 rows, found {len(df)}")
        
    # 3. Missing values check
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        issues.append(f"Found {null_count} missing values across the dataset")
        
    # 4. Duplicate rows check
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        issues.append(f"Found {dup_count} duplicate rows")
        
    # 5. Total birth count benchmark
    if "Births" in df.columns:
        total_births = int(df["Births"].sum())
        if total_births != 3604640:
            issues.append(f"Total births ({total_births:,}) differed from expected 3,604,640")
            
    is_valid = len(issues) == 0
    return is_valid, issues


@st.cache_data(show_spinner="Loading provisional natality data...")
def load_natality_data() -> pd.DataFrame:
    """
    Loads and preprocesses the 2025 CDC Provisional Natality workbook.
    Cached via Streamlit to ensure the workbook is only read from disk once.
    """
    file_path = get_data_path()
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {file_path}. Please verify the file path."
        )

    # Read the active sheet (sheet 0)
    df = pd.read_excel(file_path, sheet_name=0)

    # Validate dataset integrity
    is_valid, validation_issues = validate_dataset(df)
    if not is_valid:
        raise ValueError(f"Dataset validation failed: {'; '.join(validation_issues)}")

    # Add 2-letter state postal abbreviation for spatial mapping
    df["State Abbrev"] = df["State of Residence"].map(STATE_TO_ABBREV)

    # Ensure Month is an ordered categorical to guarantee calendar ordering in charts
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    return df
