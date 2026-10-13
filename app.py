import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Road Accident Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- MODERN UI STYLE ----------------
st.markdown("""
<style>
    .stApp {
        background: #f5f6fb;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8eaf2;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .dashboard-header {
        background: linear-gradient(115deg, #312e81, #7048e8);
        padding: 28px 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
    }

    .dashboard-header h1 {
        color: white;
        font-size: 30px;
        margin: 0;
    }

    .dashboard-header p {
        color: #e9e7ff;
        margin: 8px 0 0 0;
        font-size: 15px;
    }

    .kpi-card {
        background: white;
        border: 1px solid #e9eaf2;
        border-radius: 16px;
        padding: 20px;
        min-height: 125px;
        box-shadow: 0 3px 14px rgba(35, 35, 80, 0.04);
    }

    .kpi-label {
        color: #747994;
        font-size: 14px;
        margin-bottom: 10px;
    }

    .kpi-value {
        color: #202342;
        font-size: 27px;
        font-weight: 750;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }

    .kpi-note {
        color: #8589a0;
        font-size: 12px;
        margin-top: 9px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border-radius: 16px;
        border-color: #e9eaf2;
    }

    h2, h3 {
        color: #252747;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e9eaf2;
        padding: 15px;
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("RA2019_A2.csv")
    data.columns = data.columns.str.strip()

    if "States/UTs" not in data.columns:
        raise ValueError(
            "The dataset does not contain a 'States/UTs' column."
        )

    data["States/UTs"] = (
        data["States/UTs"].astype(str).str.strip()
    )

    return data


try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.info(
        "Make sure RA2019_A2.csv is in the same folder as app.py."
    )
    st.stop()


# ---------------- FIND YEAR COLUMNS ----------------
def find_accident_column(year):
    matches = [
        col for col in df.columns
        if "Total Number of Road Accidents during" in col
        and str(year) in col
        and "Rank" not in col
        and "Share of" not in col
    ]

    return matches[0] if matches else None


year_columns = {
    year: find_accident_column(year)
    for year in range(2016, 2020)
}

available_years = [
    year for year, col in year_columns.items()
    if col is not None
]

if not available_years:
    st.error("No road accident year columns were found.")
    st.write("Dataset columns:", df.columns.tolist())
    st.stop()


# ---------------- PREPARE STATE DATA ----------------
def get_state_data(year):
    column = year_columns[year]

    result = df.loc[
        df["States/UTs"].str.casefold() != "total",
        ["States/UTs", column]
    ].copy()

    result[column] = pd.to_numeric(
        result[column], errors="coerce"
    )

    result = result.dropna(subset=[column])

    result = result.rename(
        columns={column: "Accidents"}
    )

    return result


# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🚦 Accident Analytics")
st.sidebar.caption("India · 2016–2019")
st.sidebar.divider()

selected_year = st.sidebar.selectbox(
    "📅 Select year",
    available_years,
    index=len(available_years) - 1
)

state_data = get_state_data(selected_year)

state_options = ["All States/UTs"] + sorted(
    state_data["States/UTs"].unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "📍 Select state / UT",
    state_options
)

st.sidebar.divider()
st.sidebar.caption("Data source: RA2019_A2.csv")
st.sidebar.caption("Project: Road Accident Analysis in India")


# ---------------- CALCULATE YEAR TOTALS ----------------
year_totals = {}

for year in available_years:
    year_totals[year] = int(
        get_state_data(year)["Accidents"].sum()
    )

total_accidents = year_totals[selected_year]

top_state_row = state_data.loc[
    state_data["Accidents"].idxmax()
]

highest_state = top_state_row["States/UTs"]
highest_state_value = int(top_state_row["Accidents"])

previous_year = selected_year - 1
year_change = None

if previous_year in year_totals:
    previous_total = year_totals[previous_year]

    if previous_total != 0:
        year_change = (
            (total_accidents - previous_total)
            / previous_total
        ) * 100


# ---------------- HEADER ----------------
st.markdown("""
<div class="dashboard-header">
    <h1>🚦 Road Accident Analytics</h1>
    <p>
        India Road Accident Analysis · Interactive Dashboard
        · 2016–2019
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"### Dashboard Overview — {selected_year}")


# ---------------- KPI CARDS ----------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Reported Accidents</div>
        <div class="kpi-value">{total_accidents:,}</div>
        <div class="kpi-note">Selected year: {selected_year}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">States / UTs in Dataset</div>
        <div class="kpi-value">
            {state_data["States/UTs"].nunique()}
        </div>
        <div class="kpi-note">Available state-level records</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Highest Reported State/UT</div>
        <div class="kpi-value" style="font-size:22px">
            {highest_state}
        </div>
        <div class="kpi-note">
            {highest_state_value:,} reported accidents
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    change_text = (
        f"{year_change:+.2f}%"
        if year_change is not None
        else "N/A"
    )

    change_note = (
        f"Compared with {previous_year}"
        if year_change is not None
        else "Previous year not available"
    )

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Year-on-Year Change</div>
        <div class="kpi-value" style="font-size:27px">
            {change_text}
        </div>
        <div class="kpi-note">{change_note}</div>
    </div>
    """, unsafe_allow_html=True)


st.write("")
st.divider()


# ---------------- CHARTS ----------------
left, right = st.columns([1.2, 1])

with left:
    st.markdown("### 📈 Accident Trends")

    trend_years = available_years
    trend_values = [
        year_totals[year] for year in trend_years
    ]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(
        trend_years,
        trend_values,
        marker="o",
        linewidth=3,
        markersize=8,
        color="#7048e8"
    )

    for x, y in zip(trend_years, trend_values):
        ax.annotate(
            f"{y:,}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9
        )

    ax.set_xticks(trend_years)
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda value, pos: f"{int(value):,}"
        )
    )
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_xlabel("Year")
    ax.set_ylabel("Reported accidents")
    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.markdown(f"### 🏆 Top 10 States/UTs — {selected_year}")

    top10 = state_data.nlargest(
        10, "Accidents"
    ).sort_values("Accidents", ascending=True)

    fig, ax = plt.subplots(figsize=(7, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bars = ax.barh(
        top10["States/UTs"],
        top10["Accidents"],
        color="#7048e8",
        height=0.68
    )

    ax.bar_label(
        bars,
        labels=[f"{int(v):,}" for v in top10["Accidents"]],
        padding=3,
        fontsize=8
    )

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda value, pos: f"{int(value):,}"
        )
    )
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_xlabel("Reported accidents")
    ax.set_ylabel("")
    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


st.divider()


# ---------------- STATE DETAILS ----------------
st.markdown("### 📍 State-wise Analysis")

if selected_state == "All States/UTs":
    display_data = state_data.sort_values(
        "Accidents", ascending=False
    ).copy()

    st.caption(
        f"All available state/UT records for {selected_year}"
    )

else:
    display_data = state_data[
        state_data["States/UTs"] == selected_state
    ].copy()

    st.caption(
        f"Selected state/UT: {selected_state} · {selected_year}"
    )

    if not display_data.empty:
        st.metric(
            f"Reported accidents in {selected_state}",
            f"{int(display_data['Accidents'].iloc[0]):,}"
        )


display_data = display_data.rename(
    columns={
        "States/UTs": "State / UT",
        "Accidents": "Reported Accidents"
    }
)

st.dataframe(
    display_data.reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)


# ---------------- YEAR SUMMARY TABLE ----------------
st.divider()
st.markdown("### 📊 Year-wise Summary")

summary_data = pd.DataFrame({
    "Year": available_years,
    "Total Reported Accidents": [
        year_totals[year] for year in available_years
    ]
})

st.dataframe(
    summary_data,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Note: Totals are calculated by summing state/UT records "
    "after excluding the dataset's aggregate Total row. "
    "Results depend on the supplied dataset."
)