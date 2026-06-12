import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

    df["Transfer_Efficiency"]     = df["CBP_Transferred"] / df["CBP_InCustody"].replace(0, float("nan"))
    df["Discharge_Effectiveness"] = df["HHS_Discharged"]  / df["HHS_InCare"].replace(0, float("nan"))
    df["Pipeline_Throughput"]     = df["HHS_Discharged"] / df["CBP_Apprehended"].replace(0, float("nan"))
    df["Backlog"] = df["HHS_InCare"] - df["HHS_Discharged"]

    return df

df = load_data()

# -------------------------------
# Sidebar Filters
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
# KPIs
# -------------------------------
st.subheader("📊 Key Performance Indicators")

avg_te = df_f["Transfer_Efficiency"].mean()
avg_de = df_f["Discharge_Effectiveness"].mean()
avg_pt = df_f["Pipeline_Throughput"].mean()
avg_bl = df_f["Backlog"].mean()
oss    = df_f["Discharge_Effectiveness"].std()

kpi_df = pd.DataFrame([{
    "Transfer Efficiency":     f"{avg_te:.2%}" if pd.notna(avg_te) else "N/A",
    "Discharge Effectiveness": f"{avg_de:.2%}" if pd.notna(avg_de) else "N/A",
    "Pipeline Throughput":     f"{avg_pt:.2%}" if pd.notna(avg_pt) else "N/A",
    "Avg Backlog":             f"{avg_bl:,.0f}",
    "Outcome Stability (std)": f"{oss:.4f}" if pd.notna(oss) else "N/A"
}])

st.dataframe(kpi_df, width="stretch")
st.markdown("---")

# -------------------------------
# Care Pipeline Flow
# -------------------------------
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
fig1.update_layout(title="Daily Pipeline Volumes (Filtered)", xaxis_title="Date", yaxis_title="Children", height=400)
st.plotly_chart(fig1, width="stretch")

# -------------------------------
# Efficiency Panels
# -------------------------------
st.subheader("⚙️ Transfer & Discharge Efficiency")
col1, col2 = st.columns(2)
with col1:
    fig2 = px.line(df_f, x="Date", y="Transfer_Efficiency", title="Transfer Efficiency Ratio")
    fig2.add_hline(y=transfer_threshold, line_dash="dash", line_color="orange", annotation_text="Threshold")
    st.plotly_chart(fig2, width="stretch")
with col2:
    fig3 = px.line(df_f, x="Date", y="Discharge_Effectiveness", title="Discharge Effectiveness")
    fig3.add_hline(y=discharge_threshold, line_dash="dash", line_color="orange", annotation_text="Threshold")
    st.plotly_chart(fig3, width="stretch")

# -------------------------------
# Backlog Detection
# -------------------------------
st.subheader("🚨 Backlog & Delay Detection")
backlog_color = df_f["Backlog"].apply(lambda x: "red" if x > backlog_threshold else "steelblue")
fig4 = go.Figure()
fig4.add_trace(go.Bar(x=df_f["Date"], y=df_f["Backlog"], marker_color=backlog_color.tolist(), name="Backlog"))
fig4.add_hline(y=backlog_threshold, line_dash="dash", line_color="orange", annotation_text=f"Threshold: {backlog_threshold:,}")
fig4.update_layout(title="Daily Backlog (Filtered)", xaxis_title="Date", yaxis_title="Children", height=380)
st.plotly_chart(fig4, width="stretch")

# -------------------------------
# Outcome Trends
# -------------------------------
st.subheader("📅 Outcome Trends")
monthly = df_f.groupby(df_f["Date"].dt.to_period("M")).agg(
    Avg_HHS_InCare=("HHS_InCare","mean"),
    Avg_Discharged=("HHS_Discharged","mean"),
    Avg_Transfer_Eff=("Transfer_Efficiency","mean"),
    Avg_Discharge_Eff=("Discharge_Effectiveness","mean"),
).reset_index()
monthly["Month"] = monthly["Date"].astype(str)

col3, col4 = st.columns(2)
with col3:
    fig5 = px.bar(monthly, x="Month", y=["Avg_HHS_InCare","Avg_Discharged"], barmode="group", title="HHS In Care vs Discharged")
    fig5.update_xaxes(tickangle=45)
    st.plotly_chart(fig5, width="stretch")
with col4:
    fig6 = px.line(monthly, x="Month", y=["Avg_Transfer_Eff","Avg_Discharge_Eff"], title="Monthly Efficiency Ratios")
    fig6.update_xaxes(tickangle=45)
    st.plotly_chart(fig6, width="stretch")

# -------------------------------
# Raw Data
# -------------------------------
st.subheader("📋 Raw Data (Filtered)")
st.dataframe(df_f.reset_index(drop=True), width="stretch")
st.download_button("⬇️ Download Filtered Data", df_f.to_csv(index=False), file_name="uac_filtered.csv", mime="text/csv")

st.markdown("---")
st.caption("UAC Care Transition Analytics Dashboard | HHS Data | Unified Mentor Project")