import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ---------------- DB CONNECTION ----------------
# Update with your DB credentials
engine = create_engine("sqlite:///customer360.db")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    query = """
    SELECT 
        c.customer_id,
        c.name,
        c.country,
        SUM(t.amount) AS total_spent,
        COUNT(t.transaction_id) AS frequency
    FROM customers c
    JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.name, c.country
    """
    return pd.read_sql(query, engine)

df = load_data()

# ---------------- TITLE ----------------
st.title("🚀 Customer 360° Intelligence Dashboard")

# ---------------- KPI SECTION ----------------
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", len(df))
col2.metric("Total Revenue", f"${df['total_spent'].sum():,.2f}")
col3.metric("Avg Spend", f"${df['total_spent'].mean():,.2f}")

# ---------------- CUSTOMER SEGMENTATION ----------------
st.subheader("🎯 Customer Segmentation")

def segment(row):
    if row > 800:
        return "High Value"
    elif row > 400:
        return "Medium Value"
    else:
        return "Low Value"

df["segment"] = df["total_spent"].apply(segment)

segment_counts = df["segment"].value_counts()

st.bar_chart(segment_counts)

# ---------------- TOP CUSTOMERS ----------------
st.subheader("🏆 Top Customers")

top_customers = df.sort_values(by="total_spent", ascending=False).head(5)
st.dataframe(top_customers)

# ---------------- FILTER ----------------
st.subheader("🔍 Filter by Country")

country = st.selectbox("Select Country", df["country"].unique())

filtered_df = df[df["country"] == country]
st.write(filtered_df)

# ---------------- DOWNLOAD ----------------
st.download_button(
    label="📥 Download Data",
    data=filtered_df.to_csv(index=False),
    file_name="customer_data.csv",
    mime="text/csv"
)
