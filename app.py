import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# ---------------- DB CONNECTION ----------------
engine = create_engine("sqlite:///customer360.db", connect_args={"check_same_thread": False})

# ---------------- INIT DATABASE ----------------
def init_db():
    conn = sqlite3.connect("customer360.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    # Insert sample data (only if empty)
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO customers VALUES (?, ?, ?)", [
            (1, "Aman", "India"),
            (2, "Sara", "UK"),
            (3, "John", "USA")
        ])

    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?)", [
            (101, 1, 500),
            (102, 1, 700),
            (103, 2, 300),
            (104, 3, 1000)
        ])

    conn.commit()
    conn.close()

# Run DB init
init_db()

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
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.name, c.country
    """
    return pd.read_sql(query, engine)

# Safe load
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

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
    if row and row > 800:
        return "High Value"
    elif row and row > 400:
        return "Medium Value"
    else:
        return "Low Value"

df["segment"] = df["total_spent"].fillna(0).apply(segment)

st.bar_chart(df["segment"].value_counts())

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
