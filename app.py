import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="UAC Care Transition Analytics", layout="wide")

st.title("🧒 UAC Program — Care Transition Efficiency & Placement Outcome Analytics")
st.markdown("**U.S. Department of Health and Human Services | Unified Mentor Project**")
st.markdown("---")

# -------------------------------
# Load & Clean Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values("Date").reset_index(drop=True)

    df.rename(columns={
        df.columns[1]: "CBP_Apprehended",
        df.columns[2]: "CBP_InCustody",
        df.columns[3]: "CBP_Transferred",
        df.columns[4]: "HHS_InCare",
        df.columns[5]: "HHS_Discharged",
    }, inplace=True)

    for col in ["CBP_Apprehended","CBP_InCustody","CBP_Transferred","HHS_InCare","HHS_Discharged"]:
        df[col] = df[col].astype(str).str.replace(",", "").astype(float)

    # Derived metrics
    df["Transfer_Efficiency"]     = df["CBP_Transferred"] / df["CBP_InCustody"].replace(0, np.nan)
    df["Discharge_Effectiveness"] = df["HHS_Discharged"]  / df["HHS_InCare"].replace(0, np.nan)
    df["Pipeline_Throughput"]     = df["HHS_Discharged"] / df["CBP_Apprehended"].replace(0, np.nan)
    df["Backlog"] = df["HHS_InCare"] - df["HHS_Discharged"]

    return df

df = load_data()

# -------------------------------
# Sidebar Filters (Global)
# -------------------------------
st.sidebar.header("🔧 Filters")

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
start_date = pd.to_datetime(st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date))
end_date   = pd.to_datetime(st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date))

backlog_threshold   = st.sidebar.slider("⚠️ Backlog Alert Threshold", 0, 10000, 3000, 500)
transfer_threshold  = st.sidebar.slider("Transfer Efficiency Threshold", 0.0, 1.0, 0.5, 0.05)
discharge_threshold = st.sidebar.slider("Discharge Effectiveness Threshold", 0.0, 1.0, 0.5, 0.05)

df_f = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()

# -------------------------------
# Monthly Summary
# -------------------------------
@st.cache_data
def monthly_summary(df):
    monthly = df.groupby(df["Date"].dt.to_period("M")).agg(
        Avg_HHS_InCare=("HHS_InCare","mean"),
        Avg_Discharged=("HHS_Discharged","mean"),
        Avg_Transfer_Eff=("Transfer_Efficiency","mean"),
        Avg_Discharge_Eff=("Discharge_Effectiveness","mean"),
    ).reset_index()
    monthly["Month"] = monthly["Date"].astype(str)
    return monthly

monthly = monthly_summary(df_f)

# -------------------------------
# Tabs Layout
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["KPIs", "Pipeline", "Backlog", "Trends", "Forecasting"])

# -------------------------------
# KPIs
# -------------------------------
with tab1:
    st.subheader("📊 Key Performance Indicators")

    avg_te = df_f["Transfer_Efficiency"].mean()
    avg_de = df_f["Discharge_Effectiveness"].mean()
    avg_pt = df_f["Pipeline_Throughput"].mean()
    avg_bl = df_f["Backlog"].mean()

    def styled_metric(label, value, threshold, higher_is_better=True):
        if pd.notna(value):
            color = "green" if (value >= threshold if higher_is_better else value <= threshold) else "red"
            st.markdown(f"<div style='color:{color}; font-size:18px; font-weight:bold;'>{label}: {value:.2%}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"{label}: N/A")

    col1, col2, col3 = st.columns(3)
    with col1:
        styled_metric("Transfer Efficiency", avg_te, transfer_threshold)
        st.metric("Pipeline Throughput", f"{avg_pt:.2%}" if pd.notna(avg_pt) else "N/A")
    with col2:
        styled_metric("Discharge Effectiveness", avg_de, discharge_threshold)
    with col3:
        styled_metric("Avg Backlog", avg_bl, backlog_threshold, higher_is_better=False)

# -------------------------------
# Pipeline Flow
# -------------------------------
with tab2:
    st.subheader("🔄 Care Pipeline Flow")
    fig1 = go.Figure()
    for col, name in [
        ("CBP_Apprehended","CBP Apprehended"),
        ("CBP_InCustody","CBP In Custody"),
        ("CBP_Transferred","Transferred to HHS"),
        ("HHS_InCare","HHS In Care"),
        ("HHS_Discharged","HHS Discharged")
    ]:
        fig1.add_trace(go.Scatter(x=df_f["Date"], y=df_f[col], name=name, mode="lines"))
    st.plotly_chart(fig1)

# -------------------------------
# Backlog Detection
# -------------------------------
with tab3:
    st.subheader("🚨 Backlog & Delay Detection")
    backlog_color = df_f["Backlog"].apply(lambda x: "red" if x > backlog_threshold else "steelblue")
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=df_f["Date"], y=df_f["Backlog"], marker_color=backlog_color.tolist(), name="Backlog"))
    fig4.add_hline(y=backlog_threshold, line_dash="dash", line_color="orange", annotation_text=f"Threshold: {backlog_threshold:,}")
    st.plotly_chart(fig4)

# -------------------------------
# Trends
# -------------------------------
with tab4:
    st.subheader("📅 Outcome Trends")
    col3, col4 = st.columns(2)
    with col3:
        fig5 = px.bar(monthly, x="Month", y=["Avg_HHS_InCare","Avg_Discharged"], barmode="group", title="HHS In Care vs Discharged")
        st.plotly_chart(fig5)
    with col4:
        fig6 = px.line(monthly, x="Month", y=["Avg_Transfer_Eff","Avg_Discharge_Eff"], title="Monthly Efficiency Ratios")
        st.plotly_chart(fig6)

# -------------------------------
# Forecasting (Random Forest + Prophet Combined)
# -------------------------------
with tab5:
    st.subheader("📈 Forecasting Future Discharges (Combined Models)")

    ml_df = df_f.dropna(subset=["HHS_Discharged"]).copy()
    ml_df["DayOfWeek"] = ml_df["Date"].dt.dayofweek
    ml_df["Month"] = ml_df["Date"].dt.month
    y = ml_df["HHS_Discharged"]

    if len(ml_df) > 30:
        # --- Random Forest ---
        X = ml_df[["CBP_Apprehended","CBP_InCustody","CBP_Transferred","HHS_InCare","DayOfWeek","Month"]]
        rf = RandomForestRegressor(n_estimators=200, random_state=42)
        rf.fit(X, y)

        last_row = X.iloc[-1]
        future_X = pd.DataFrame([last_row.values] * 30, columns=X.columns)
        rf_preds = rf.predict(future_X)

        forecast_dates = pd.date_range(ml_df["Date"].iloc[-1] + pd.Timedelta(days=1), periods=30, freq="D")
        rf_forecast_df = pd.DataFrame({"Date": forecast_dates, "RandomForest": rf_preds})

        # --- Prophet ---
        prophet_df = ml_df[["Date","HHS_Discharged"]].rename(columns={"Date":"ds","HHS_Discharged":"y"})
        m = Prophet()
        m.fit(prophet_df)
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

        prophet_forecast_df = forecast[["ds","yhat","yhat_lower","yhat_upper"]].tail(30)
        prophet_forecast_df.rename(columns={"ds":"Date","yhat":"Prophet"}, inplace=True)

        # --- Combined Chart ---
        fig_combined = go.Figure()

        # Actuals
        fig_combined.add_trace(go.Scatter(x=ml_df["Date"], y=y, mode="lines", name="Actual"))

        # Random Forest forecast
        fig_combined.add_trace(go.Scatter(x=rf_forecast_df["Date"], y=rf_forecast_df["RandomForest"],
            mode="lines", name="Random Forest"))

        # Prophet forecast
        fig_combined.add_trace(go.Scatter(x=prophet_forecast_df["Date"], y=prophet_forecast_df["Prophet"],
            mode="lines", name="Prophet"))

        # Prophet confidence intervals
        fig_combined.add_trace(go.Scatter(x=prophet_forecast_df["Date"], y=prophet_forecast_df["yhat_upper"],
            mode="lines", line=dict(dash="dot", color="lightblue"), name="Prophet Upper CI"))
        
        fig_combined.add_trace(go.Scatter(x=prophet_forecast_df["Date"], y=prophet_forecast_df["yhat_lower"],
            mode="lines", line=dict(dash="dot", color="lightblue"), name="Prophet Lower CI"))

        fig_combined.update_layout(title="Random Forest vs Prophet Forecast (Next 30 Days)",
            xaxis_title="Date", yaxis_title="Forecasted Discharges")

        st.plotly_chart(fig_combined)