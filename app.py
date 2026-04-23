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
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        country TEXT,
        age INTEGER,
        gender TEXT,
        signup_date DATE
    );

    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL,
        transaction_date DATE
    );
    """)

    # Insert only if empty
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, 'Aman', 'aman@gmail.com', 'India', 25, 'Male', '2023-01-10'),
            (2, 'Sara', 'sara@gmail.com', 'UK', 30, 'Female', '2023-02-15'),
            (3, 'John', 'john@gmail.com', 'USA', 28, 'Male', '2023-03-20'),
            (4, 'Priya', 'priya@gmail.com', 'India', 27, 'Female', '2023-04-12'),
            (5, 'David', 'david@gmail.com', 'Germany', 35, 'Male', '2023-05-05')
        ])

    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO transactions VALUES (?, ?, ?, ?)
        """, [
            (101, 1, 500, '2023-06-01'),
            (102, 1, 700, '2023-07-01'),
            (103, 2, 300, '2023-06-10'),
            (104, 3, 1000, '2023-07-05'),
            (105, 4, 450, '2023-07-10'),
            (106, 5, 800, '2023-07-15')
        ])

    conn.commit()
    conn.close()

init_db()

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    query = """
    SELECT 
        c.customer_id,
        c.name,
        c.country,
        COALESCE(SUM(t.amount), 0) AS total_spent,
        COUNT(t.transaction_id) AS frequency
    FROM customers c
    LEFT JOIN transactions t 
    ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.name, c.country
    """
    return pd.read_sql(query, engine)

df = load_data()

# ---------------- UI ----------------
st.title("🚀 Customer 360° Intelligence Dashboard")

# KPIs
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", len(df))
col2.metric("Total Revenue", f"${df['total_spent'].sum():,.2f}")
col3.metric("Avg Spend", f"${df['total_spent'].mean():,.2f}")

# Segmentation
st.subheader("🎯 Customer Segmentation")

def segment(x):
    if x > 800:
        return "High Value"
    elif x > 400:
        return "Medium Value"
    else:
        return "Low Value"

df["segment"] = df["total_spent"].apply(segment)
st.bar_chart(df["segment"].value_counts())

# Top customers
st.subheader("🏆 Top Customers")
st.dataframe(df.sort_values(by="total_spent", ascending=False).head(5))

# Filter
st.subheader("🔍 Filter by Country")
country = st.selectbox("Select Country", df["country"].unique())
filtered_df = df[df["country"] == country]
st.dataframe(filtered_df)

# Download
# ---------------- DOWNLOAD (CENTERED) ----------------
st.subheader("")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.download_button(
        label="📥 Download Data",
        data=filtered_df.to_csv(index=False),
        file_name="customer_data.csv",
        mime="text/csv"
    )
