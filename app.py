import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# ---------------- DB CONNECTION ----------------
engine = create_engine("sqlite:///customer360.db", connect_args={"check_same_thread": False})

# ---------------- INIT DATABASE ----------------
import sqlite3

def init_db():
    conn = sqlite3.connect("customer360.db")
    cursor = conn.cursor()

    cursor.executescript("""
    -- CUSTOMERS
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        country TEXT,
        age INTEGER,
        gender TEXT,
        signup_date DATE
    );

    -- TRANSACTIONS
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL,
        transaction_date DATE
    );

    -- CAMPAIGNS
    CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY,
        campaign_name TEXT,
        channel TEXT,
        start_date DATE,
        end_date DATE
    );

    -- INTERACTIONS
    CREATE TABLE IF NOT EXISTS interactions (
        interaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        campaign_id INTEGER,
        interaction_type TEXT,
        interaction_date DATE
    );

    INSERT OR IGNORE INTO customers VALUES
    (1, 'Aman', 'aman@gmail.com', 'India', 25, 'Male', '2023-01-10'),
    (2, 'Sara', 'sara@gmail.com', 'UK', 30, 'Female', '2023-02-15'),
    (3, 'John', 'john@gmail.com', 'USA', 28, 'Male', '2023-03-20'),
    (4, 'Priya', 'priya@gmail.com', 'India', 27, 'Female', '2023-04-12'),
    (5, 'David', 'david@gmail.com', 'Germany', 35, 'Male', '2023-05-05');

    INSERT OR IGNORE INTO transactions VALUES
    (101, 1, 500, '2023-06-01'),
    (102, 1, 700, '2023-07-01'),
    (103, 2, 300, '2023-06-10'),
    (104, 3, 1000, '2023-07-05'),
    (105, 4, 450, '2023-07-10'),
    (106, 5, 800, '2023-07-15');

    INSERT OR IGNORE INTO campaigns VALUES
    (201, 'Summer Sale', 'Email', '2023-06-01', '2023-06-30'),
    (202, 'Festive Ads', 'Social', '2023-07-01', '2023-07-31'),
    (203, 'Black Friday', 'Ads', '2023-11-01', '2023-11-30');

    INSERT OR IGNORE INTO interactions VALUES
    (301, 1, 201, 'click', '2023-06-02'),
    (302, 1, 201, 'purchase', '2023-06-03'),
    (303, 2, 202, 'open', '2023-07-02'),
    (304, 3, 202, 'click', '2023-07-03'),
    (305, 4, 203, 'purchase', '2023-11-10'),
    (306, 5, 203, 'click', '2023-11-15');
    """)

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
