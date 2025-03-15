import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(page_title="Loan Product Analysis", layout="wide")

# Custom CSS for better styling
st.markdown(
    """
    <style>
        body {background-color: #121212; color: #ffffff;}
        .stApp {background: #1e1e1e; color: #ffffff;}
        .stDataFrame {background: #2a2a2a; color: #ffffff;}
        .stAlert {background-color: #333333; color: white; border-radius: 10px; padding: 15px;}
        .header {text-align: center; font-size: 24px; font-weight: bold; color: #FFD700;}
        .progress-bar {background-color: #555555; border-radius: 10px; padding: 5px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# 🎯 App Title
st.markdown('<p class="header">📊 Loan Product Performance Dashboard</p>', unsafe_allow_html=True)

# 📌 Required fields information
st.markdown('<div class="stAlert">📌 **Before uploading, ensure your CSV has the following fields:**</div>', unsafe_allow_html=True)
st.write(
    "- `Loan_ID` (Unique identifier for each loan)\n"
    "- `Loan_Amount` (Numeric value for the loan amount issued)\n"
    "- `Date_Granted` (Date when the loan was granted, format: **DD-MM-YYYY**)\n"
    "- `Loan_Type` (Type/category of the loan)"
)

# 📂 File uploader
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)

    # Show raw data preview
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())

    # Ensure necessary columns exist
    required_columns = ["Loan_ID", "Loan_Amount", "Date_Granted", "Loan_Type"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"🚨 Missing columns: {', '.join(missing_columns)}. Please upload a correct CSV file.")
    else:
        # Convert Date_Granted to datetime format (DD-MM-YYYY)
        df["Date_Granted"] = pd.to_datetime(df["Date_Granted"], format="%d-%m-%Y", errors="coerce")

        # Convert Loan_Amount to numeric
        df["Loan_Amount"] = pd.to_numeric(df["Loan_Amount"], errors="coerce").fillna(0)

        # Normalize Loan_Type column
        df["Loan_Type"] = df["Loan_Type"].astype(str).str.strip().str.lower()

        # Ensure every Loan_Type appears in groupby
        all_loan_types = df["Loan_Type"].unique()
        default_data = pd.DataFrame({"Loan_Type": all_loan_types})

        ### 🚀 Loan Product Popularity by Count ###
        st.subheader("📌 Loan Product Popularity (Number of Loans Issued)")
        product_count = df.groupby("Loan_Type", as_index=False)["Loan_ID"].count()
        product_count.columns = ["Loan_Type", "Count"]
        product_count = default_data.merge(product_count, on="Loan_Type", how="left").fillna(0)
        product_count["Count"] = product_count["Count"].astype(int)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=product_count, x="Loan_Type", y="Count", palette="coolwarm", ax=ax)
        ax.set_title("Loan Product Popularity by Count", fontsize=14, color="black", fontweight="bold")
        plt.xticks(rotation=45, color="black", fontsize=10, fontweight="bold")
        plt.yticks(color="black", fontsize=10, fontweight="bold")
        st.pyplot(fig)

        ### 💰 Loan Product Popularity by Amount Disbursed ###
        st.subheader("💵 Loan Product Popularity (Total Amount Disbursed)")
        product_amount = df.groupby("Loan_Type", as_index=False)["Loan_Amount"].sum()
        product_amount.columns = ["Loan_Type", "Total_Amount"]
        product_amount = default_data.merge(product_amount, on="Loan_Type", how="left").fillna(0)
        product_amount["Total_Amount"] = product_amount["Total_Amount"].astype(float)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=product_amount, x="Loan_Type", y="Total_Amount", color="orange", ax=ax)
        ax.set_title("Loan Product Popularity by Amount Disbursed", fontsize=14, color="black", fontweight="bold")
        plt.xticks(rotation=45, color="black", fontsize=10, fontweight="bold")
        plt.yticks(color="black", fontsize=10, fontweight="bold")
        st.pyplot(fig)

        ### 📈 Monthly Loan Disbursement Trend ###
        st.subheader("📅 Loan Disbursement Trend Over Time")
        df["Month"] = df["Date_Granted"].dt.to_period("M")
        monthly_summary = df.groupby("Month")["Loan_Amount"].sum().reset_index()
        monthly_summary["Month"] = monthly_summary["Month"].astype(str)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=monthly_summary, x="Month", y="Loan_Amount", marker="o", color="blue", ax=ax)
        ax.set_title("Loan Performance Trend", fontsize=14, color="black", fontweight="bold")
        plt.xticks(rotation=45, color="black", fontsize=10, fontweight="bold")
        plt.yticks(color="black", fontsize=10, fontweight="bold")
        st.pyplot(fig)

        ### 📊 Loan Product-Specific Statistics ###
        st.subheader("📌 Loan Product Summary Statistics")
        product_stats = df.groupby("Loan_Type").agg(
            Total_Loans=("Loan_ID", "count"),
            Total_Amount=("Loan_Amount", "sum"),
            Avg_Amount=("Loan_Amount", "mean"),
            Max_Amount=("Loan_Amount", "max"),
            Min_Amount=("Loan_Amount", "min")
        ).reset_index()

        # Calculate portfolio percentage
        total_loans_disbursed = product_stats["Total_Amount"].sum()
        product_stats["Portfolio_Percentage"] = (product_stats["Total_Amount"] / total_loans_disbursed) * 100

        # Format numbers with comma separators
        product_stats["Total_Amount"] = product_stats["Total_Amount"].map("{:,.2f}".format)
        product_stats["Avg_Amount"] = product_stats["Avg_Amount"].map("{:,.2f}".format)
        product_stats["Max_Amount"] = product_stats["Max_Amount"].map("{:,.2f}".format)
        product_stats["Min_Amount"] = product_stats["Min_Amount"].map("{:,.2f}".format)
        product_stats["Portfolio_Percentage"] = product_stats["Portfolio_Percentage"].map("{:.2f}%".format)

        st.dataframe(product_stats)

st.write("📥 Upload a CSV file to analyze loan product performance.")
