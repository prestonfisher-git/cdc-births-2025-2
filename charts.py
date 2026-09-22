"""
Plotly Visualizations Module for CDC Provisional Natality 2025 Dashboard.

Follows accessibility, clear zero-baseline axes, thousands number formatting,
and responsive styling for undergraduate analytics students.
"""

from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Professional accessible color palette (high-contrast, colorblind-friendly)
COLOR_PRIMARY = "#1E3A8A"     # Deep Navy
COLOR_SECONDARY = "#0D9488"   # Deep Teal
COLOR_ACCENT = "#D97706"      # Warm Amber
COLOR_FEMALE = "#7C3AED"      # Iris / Violet (Accessible, avoids stereotype pink)
COLOR_MALE = "#0284C7"        # Cerulean / Sky Blue (Accessible)
CHOROPLETH_SCALE = "Blues"    # Intuitive sequential gradient for geographic volume
HEATMAP_SCALE = "YlGnBu"      # Yellow-Green-Blue sequential gradient


def apply_standard_layout(
    fig: go.Figure,
    title: str,
    subtitle: Optional[str] = None,
    height: int = 450
) -> go.Figure:
    """Applies a consistent, clean, and accessible theme to Plotly figures."""
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size: 12px; color: #64748B;'>{subtitle}</span>"

    fig.update_layout(
        title=dict(text=full_title, x=0.01, y=0.96, xanchor="left", yanchor="top"),
        template="plotly_white",
        height=height,
        margin=dict(l=40, r=40, t=70, b=40),
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size=12),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text=""
        ),
    )
    return fig


def plot_monthly_trend(df_monthly: pd.DataFrame) -> go.Figure:
    """
    Renders the chronological monthly birth trajectory across all selected filters.
    Includes markers, zero-baseline, and formatted hover data.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_monthly["Month"],
            y=df_monthly["Births"],
            mode="lines+markers+text",
            line=dict(color=COLOR_PRIMARY, width=3),
            marker=dict(size=8, color=COLOR_SECONDARY),
            text=[f"{val:,.0f}" for val in df_monthly["Births"]],
            textposition="top center",
            textfont=dict(size=10, color="#1E293B"),
            hovertemplate="<b>%{x}</b><br>Births: <b>%{y:,.0f}</b><extra></extra>",
            name="Total Births"
        )
    )

    fig = apply_standard_layout(
        fig,
        title="Monthly Birth Count Trajectory (2025)",
        subtitle="Tracking seasonal delivery volume across the selected geographies",
        height=420
    )
    fig.update_yaxes(
        title="Total Birth Count",
        tickformat=",d",
        rangemode="tozero",
        gridcolor="#E2E8F0"
    )
    fig.update_xaxes(title="Month (Chronological)", gridcolor="#F1F5F9")
    return fig


def plot_monthly_sex_comparison(df_sex: pd.DataFrame) -> go.Figure:
    """
    Renders side-by-side comparative bars of Female vs. Male births by month.
    Demonstrates biological birth ratios and seasonal volume shifts.
    """
    fig = px.bar(
        df_sex,
        x="Month",
        y="Births",
        color="Sex of Infant",
        barmode="group",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        text_auto=",.0f"
    )

    fig = apply_standard_layout(
        fig,
        title="Monthly Births by Infant Sex",
        subtitle="Comparing male and female birth counts across months (zero-baseline enforced)",
        height=450
    )
    fig.update_traces(
        textposition="outside",
        textfont_size=10,
        hovertemplate="<b>%{x}</b> (%{data.name})<br>Births: <b>%{y:,.0f}</b><extra></extra>"
    )
    fig.update_yaxes(
        title="Birth Count",
        tickformat=",d",
        rangemode="tozero",
        gridcolor="#E2E8F0"
    )
    fig.update_xaxes(title="Month")
    return fig


def plot_sex_donut(df: pd.DataFrame) -> go.Figure:
    """
    Renders an accessible donut chart showing the overall Female vs. Male split.
    """
    sex_totals = (
        df.groupby("Sex of Infant")["Births"]
        .sum()
        .reset_index()
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=sex_totals["Sex of Infant"],
                values=sex_totals["Births"],
                hole=0.55,
                marker=dict(colors=[COLOR_FEMALE if s == "Female" else COLOR_MALE for s in sex_totals["Sex of Infant"]]),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Births: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig = apply_standard_layout(
        fig,
        title="Infant Sex Distribution",
        subtitle="Proportion of female vs. male births in active selection",
        height=380
    )
    return fig


def plot_state_ranking(df_state: pd.DataFrame) -> go.Figure:
    """
    Renders a full horizontal ranking bar chart of all selected states, sorted descending.
    """
    # Sort ascending for horizontal bar chart so highest appears at the top
    df_sorted = df_state.sort_values(by="Births", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df_sorted["Births"],
            y=df_sorted["State of Residence"],
            orientation="h",
            marker=dict(color=COLOR_PRIMARY),
            hovertemplate="<b>%{y}</b><br>Total Births: <b>%{x:,.0f}</b><extra></extra>",
            text=[f"{val:,.0f}" for val in df_sorted["Births"]],
            textposition="auto",
            textfont=dict(size=10, color="white")
        )
    )

    dynamic_height = max(450, len(df_sorted) * 22)

    fig = apply_standard_layout(
        fig,
        title="Geographic Ranking by Total Birth Count",
        subtitle="States ordered by cumulative volume in selected timeframe",
        height=dynamic_height
    )
    fig.update_xaxes(
        title="Total Birth Count",
        tickformat=",d",
        rangemode="tozero",
        gridcolor="#E2E8F0"
    )
    fig.update_yaxes(title="State of Residence", dtick=1)
    return fig


def plot_top_bottom_states(df_state: pd.DataFrame, n: int = 5) -> go.Figure:
    """
    Compares the Top N and Bottom N geographies to illustrate volume disparity.
    """
    if len(df_state) <= n * 2:
        top_subset = df_state.copy()
        top_subset["Category"] = "Selected Geographies"
        combined = top_subset
    else:
        top_n = df_state.head(n).copy()
        top_n["Category"] = f"Top {n} Geographies"
        bottom_n = df_state.tail(n).copy()
        bottom_n["Category"] = f"Bottom {n} Geographies"
        combined = pd.concat([top_n, bottom_n])

    combined = combined.sort_values(by="Births", ascending=True)

    colors = [
        COLOR_PRIMARY if cat.startswith("Top") else COLOR_ACCENT
        for cat in combined["Category"]
    ]

    fig = go.Figure(
        go.Bar(
            x=combined["Births"],
            y=combined["State of Residence"],
            orientation="h",
            marker=dict(color=colors),
            hovertemplate="<b>%{y}</b><br>Total Births: <b>%{x:,.0f}</b><extra></extra>",
            text=[f"{val:,.0f}" for val in combined["Births"]],
            textposition="auto",
        )
    )

    fig = apply_standard_layout(
        fig,
        title=f"Volume Disparity: Top {n} vs. Bottom {n} States",
        subtitle="Comparing high-population vs. low-population state birth counts",
        height=400
    )
    fig.update_xaxes(
        title="Total Birth Count",
        tickformat=",d",
        rangemode="tozero",
        gridcolor="#E2E8F0"
    )
    fig.update_yaxes(title="State", dtick=1)
    return fig


def plot_us_choropleth(df_state: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive US State Choropleth map using 2-letter postal abbreviations.
    Hover shows state name, births, and national share.
    """
    total_selection_births = df_state["Births"].sum()
    df_plot = df_state.copy()
    df_plot["Percent_Share"] = (
        (df_plot["Births"] / total_selection_births * 100)
        if total_selection_births > 0
        else 0
    )

    fig = px.choropleth(
        df_plot,
        locations="State Abbrev",
        locationmode="USA-states",
        color="Births",
        scope="usa",
        color_continuous_scale=CHOROPLETH_SCALE,
        hover_name="State of Residence",
        hover_data={
            "State Abbrev": False,
            "Births": ":,.0f",
            "Percent_Share": ":.2f%"
        },
        labels={"Births": "Birth Count", "Percent_Share": "Share of Selection"}
    )

    fig = apply_standard_layout(
        fig,
        title="Geographic Distribution of U.S. Births (2025)",
        subtitle="Interactive state-level map showing cumulative birth volume",
        height=520
    )
    fig.update_layout(
        geo=dict(
            lakecolor="#E0F2FE",
            landcolor="#F8FAFC",
            showlakes=True,
            projection_type="albers usa"
        ),
        coloraxis_colorbar=dict(
            title="Birth Count",
            tickformat=",d",
            len=0.75,
            y=0.5
        )
    )
    return fig


def plot_state_month_heatmap(pivot_df: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive heatmap of States (Y) by Months (X).
    Allows visual identification of seasonal delivery spikes.
    """
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="State of Residence", color="Birth Count"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale=HEATMAP_SCALE,
        aspect="auto"
    )

    fig = apply_standard_layout(
        fig,
        title="Seasonal Birth Intensity Matrix (State × Month)",
        subtitle="Heatmap of birth volume across all 12 calendar months",
        height=max(500, len(pivot_df) * 16)
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b> - %{x}<br>Birth Count: <b>%{z:,.0f}</b><extra></extra>"
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title="Births", tickformat=",d")
    )
    return fig
