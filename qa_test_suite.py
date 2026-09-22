"""
Automated Quality-Assurance Playwright Test Suite for CDC Natality 2025 Dashboard.

Executes all 12 QA test cases, validates assertions against mathematical benchmarks,
captures full-page screenshots, and produces a structured test report.
"""

import io
from pathlib import Path
import sys
import re
import pandas as pd
from playwright.sync_api import sync_playwright

# Ensure UTF-8 console output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SCREENSHOT_DIR = Path(r"C:\Users\prest\.gemini\antigravity-ide\brain\8b5aa678-3b4f-4035-9385-77542f647006\screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

test_results = []


def record_result(case_num: int, name: str, status: str, details: str):
    test_results.append({
        "Case": case_num,
        "Test Name": name,
        "Status": status,
        "Details": details
    })
    print(f"[{status}] Case {case_num}: {name} - {details}")


def run_qa_suite():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 960}, accept_downloads=True)
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        # Navigate to Dashboard
        print("Navigating to http://localhost:8501 ...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        page.wait_for_timeout(3000)

        # -------------------------------------------------------------
        # Helper selectors
        # -------------------------------------------------------------
        def get_metric_cards():
            cards = page.locator(".metric-value").all_text_contents()
            return cards

        def get_multiselect(index: int):
            return page.locator('[data-testid="stMultiSelect"]').nth(index)

        def clear_multiselect(index: int):
            ms = get_multiselect(index)
            clear_btn = ms.locator('button[aria-label="Clear all"]')
            if clear_btn.count() > 0:
                clear_btn.click()
                page.wait_for_timeout(1000)

        def add_multiselect_option(index: int, text: str):
            ms = get_multiselect(index)
            inp = ms.locator("input")
            inp.click()
            inp.fill(text)
            page.wait_for_timeout(500)
            page.locator(f'div:text-is("{text}")').click()
            page.wait_for_timeout(1000)

        def select_radio(label: str):
            page.locator('[data-testid="stRadio"] label').filter(has_text=re.compile(rf"^\s*{label}\s*$")).click()
            page.wait_for_timeout(1500)

        def click_reset():
            page.locator('button:has-text("Reset Filters")').click()
            page.wait_for_timeout(2000)

        def click_tab(tab_name_substr: str):
            page.locator(f'[data-testid="stTab"]:has-text("{tab_name_substr}")').click()
            page.wait_for_timeout(2000)

        # -------------------------------------------------------------
        # Case 1: Default dashboard with all observations
        # -------------------------------------------------------------
        cards = get_metric_cards()
        total_births = cards[0]
        geos = cards[1]
        peak_geo = cards[3]
        peak_month = cards[4]

        page.screenshot(path=str(SCREENSHOT_DIR / "01_default_dashboard.png"), full_page=True)

        if total_births == "3,604,640" and "51" in geos and peak_geo == "California" and peak_month == "July":
            record_result(1, "Default Dashboard", "PASSED", f"Total: {total_births}, Geos: {geos}, Top Geo: {peak_geo}, Peak: {peak_month}")
        else:
            record_result(1, "Default Dashboard", "FAILED", f"Unexpected values: {cards}")

        # -------------------------------------------------------------
        # Case 2: One state and all months (California)
        # -------------------------------------------------------------
        clear_multiselect(0)
        add_multiselect_option(0, "California")
        page.wait_for_timeout(1500)
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "02_one_state_all_months.png"), full_page=True)

        if cards and cards[0] == "393,111" and "1 / 51" in cards[1] and cards[3] == "California" and cards[4] == "August":
            record_result(2, "One State & All Months", "PASSED", f"CA Total: {cards[0]}, Peak: {cards[4]} ({cards[3]})")
        else:
            record_result(2, "One State & All Months", "FAILED", f"Values: {cards}")

        # -------------------------------------------------------------
        # Case 3: Several states (California, Texas, Florida, New York)
        # -------------------------------------------------------------
        add_multiselect_option(0, "Texas")
        add_multiselect_option(0, "Florida")
        add_multiselect_option(0, "New York")
        page.wait_for_timeout(1500)
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "03_several_states.png"), full_page=True)

        if cards and cards[0] == "1,203,335" and "4 / 51" in cards[1]:
            record_result(3, "Several States Filter", "PASSED", f"4 States Total: {cards[0]}, Geos: {cards[1]}")
        else:
            record_result(3, "Several States Filter", "FAILED", f"Values: {cards}")

        # -------------------------------------------------------------
        # Case 4: One month (August, All States)
        # -------------------------------------------------------------
        click_reset()
        clear_multiselect(1)
        add_multiselect_option(1, "August")
        page.wait_for_timeout(1500)
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "04_one_month.png"), full_page=True)

        if cards and cards[0] == "319,245" and cards[4] == "August":
            record_result(4, "One Month Filter", "PASSED", f"August Total: {cards[0]}, Top Geo: {cards[3]}")
        else:
            record_result(4, "One Month Filter", "FAILED", f"Values: {cards}")

        # -------------------------------------------------------------
        # Case 5: Female only
        # -------------------------------------------------------------
        click_reset()
        select_radio("Female")
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "05_female_only.png"), full_page=True)

        if cards and cards[0] == "1,762,840" and "51" in cards[1]:
            record_result(5, "Female Only Filter", "PASSED", f"Female Total: {cards[0]}")
        else:
            record_result(5, "Female Only Filter", "FAILED", f"Values: {cards}")

        # -------------------------------------------------------------
        # Case 6: Male only
        # -------------------------------------------------------------
        select_radio("Male")
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "06_male_only.png"), full_page=True)

        if cards and cards[0] == "1,841,800" and "51" in cards[1]:
            record_result(6, "Male Only Filter", "PASSED", f"Male Total: {cards[0]}")
        else:
            record_result(6, "Male Only Filter", "FAILED", f"Values: {cards}")

        # -------------------------------------------------------------
        # Case 7: Combined filter (California, August, Male)
        # -------------------------------------------------------------
        clear_multiselect(0)
        add_multiselect_option(0, "California")
        clear_multiselect(1)
        add_multiselect_option(1, "August")
        page.wait_for_timeout(1500)
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "07_combined_filter.png"), full_page=True)

        if cards and cards[0] == "17,627" and "1 / 51" in cards[1]:
            record_result(7, "Combined State, Month & Sex", "PASSED", f"CA August Male Total: {cards[0]}")
        else:
            record_result(7, "Combined State, Month & Sex", "FAILED", f"Values: {cards}")

        # -------------------------------------------------------------
        # Case 8: Reset Filters
        # -------------------------------------------------------------
        click_reset()
        cards = get_metric_cards()
        page.screenshot(path=str(SCREENSHOT_DIR / "08_reset_filters.png"), full_page=True)

        if cards and cards[0] == "3,604,640" and "51 / 51" in cards[1]:
            record_result(8, "Reset Filters Button", "PASSED", f"Reset to full dataset: {cards[0]} total births")
        else:
            record_result(8, "Reset Filters Button", "FAILED", f"Values after reset: {cards}")

        # -------------------------------------------------------------
        # Case 9: Empty or invalid selection
        # -------------------------------------------------------------
        clear_multiselect(0)
        page.wait_for_timeout(1000)
        warning_box = page.locator('[data-testid="stAlert"]').last.text_content()
        page.screenshot(path=str(SCREENSHOT_DIR / "09_empty_selection.png"), full_page=True)

        if "No observations match" in warning_box and len(console_errors) == 0:
            record_result(9, "Empty Selection Handling", "PASSED", "Defensive warning triggered cleanly without errors")
        else:
            record_result(9, "Empty Selection Handling", "FAILED", f"Warning: {warning_box}, Errors: {console_errors}")

        # -------------------------------------------------------------
        # Case 10: CSV Download
        # -------------------------------------------------------------
        click_reset()
        click_tab("Data Table & Download")
        page.wait_for_timeout(1500)

        # Trigger download
        download_btn = page.locator('[data-testid="stDownloadButton"] button, button:has-text("Download")').first
        with page.expect_download() as download_info:
            download_btn.click()
        download = download_info.value
        download_path = SCREENSHOT_DIR / download.suggested_filename
        download.save_as(str(download_path))

        # Validate downloaded CSV
        df_downloaded = pd.read_csv(download_path)
        page.screenshot(path=str(SCREENSHOT_DIR / "10_data_table_and_download.png"), full_page=True)

        if len(df_downloaded) == 1224 and df_downloaded["Births"].sum() == 3604640:
            record_result(10, "CSV Download", "PASSED", f"Downloaded {len(df_downloaded)} rows, sum: {df_downloaded['Births'].sum():,}")
        else:
            record_result(10, "CSV Download", "FAILED", f"Downloaded rows: {len(df_downloaded)}")

        # -------------------------------------------------------------
        # Case 11: Map rendering & Geographic Analysis
        # -------------------------------------------------------------
        click_tab("Geographic Analysis")
        page.wait_for_timeout(2500)
        plotly_map_count = page.locator('.js-plotly-plot').count()
        page.screenshot(path=str(SCREENSHOT_DIR / "11_geographic_analysis_map.png"), full_page=True)

        if plotly_map_count >= 3:
            record_result(11, "Map & Geographic Analysis", "PASSED", f"Rendered {plotly_map_count} interactive Plotly figures (Choropleth, Ranking, Heatmap)")
        else:
            record_result(11, "Map & Geographic Analysis", "FAILED", f"Found {plotly_map_count} charts")

        # -------------------------------------------------------------
        # Case 12: Mobile or narrow-screen layout
        # -------------------------------------------------------------
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_DIR / "12_mobile_layout.png"), full_page=True)

        title_text = page.locator("[data-testid='stMain'] h1, main h1").first.text_content()
        if "CDC Provisional Natality" in title_text and len(console_errors) == 0:
            record_result(12, "Mobile Responsive Layout", "PASSED", "Rendered cleanly on 375x812 mobile viewport without exceptions")
        else:
            record_result(12, "Mobile Responsive Layout", "FAILED", f"Title: {title_text}, Errors: {console_errors}")

        browser.close()

    print("\n--- Summary of All Test Results ---")
    df_results = pd.DataFrame(test_results)
    print(df_results.to_string(index=False))

if __name__ == "__main__":
    run_qa_suite()
