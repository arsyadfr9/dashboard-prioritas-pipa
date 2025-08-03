import streamlit as st

st.set_page_config(layout="wide")
st.title("Dashboard Prediksi Kebocoran Pipa")

# Tab 1: Pemilih Model
st.header("1. Pemilihan Model Prediksi")

model = st.radio(
    "Pilih salah satu model prediksi kebocoran:",
    [
        "Poisson - Fisik",
        "Poisson - Tekanan & Debit",
        "GBT - Fisik",
        "GBT - Tekanan & Debit"
    ]
)

st.success(f"Model yang dipilih: {model}")
