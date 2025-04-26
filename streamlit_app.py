import streamlit as st
import pandas as pd
from github import Github
import os
from datetime import datetime

# Konfigurasi GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "username/repo-name"  # Ganti dengan repo Anda
DATA_PATH = "waste_data.csv"

# Sistem poin daur ulang
POINTS_PER_KG = {
    "plastik": 10,
    "kertas": 5,
    "logam": 15,
    "kaca": 7,
    "elektronik": 20
}

def get_waste_data():
    """Ambil data dari GitHub"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        contents = repo.get_contents(DATA_PATH)
        return pd.read_csv(contents.download_url)
    except:
        return pd.DataFrame(columns=["timestamp", "username", "jenis", "berat", "poin"])

def save_waste_data(df):
    """Simpan data ke GitHub"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    contents = repo.get_contents(DATA_PATH)
    
    repo.update_file(
        path=DATA_PATH,
        message="Update waste data",
        content=df.to_csv(index=False),
        sha=contents.sha
    )

# Tampilan Streamlit
st.title("♻️ Bank Sampah Digital")

# Form input
with st.form("waste_form"):
    username = st.text_input("Nama Pengguna")
    waste_type = st.selectbox("Jenis Sampah", list(POINTS_PER_KG.keys()))
    weight = st.number_input("Berat (kg)", min_value=0.1, step=0.1)
    submitted = st.form_submit_button("Submit")

if submitted:
    if not username:
        st.error("Harap isi nama pengguna!")
    else:
        # Hitung poin
        points = weight * POINTS_PER_KG[waste_type]
        
        # Tambah ke dataframe
        new_entry = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "username": username,
            "jenis": waste_type,
            "berat": weight,
            "poin": points
        }])
        
        df = pd.concat([get_waste_data(), new_entry], ignore_index=True)
        
        # Simpan ke GitHub
        try:
            save_waste_data(df)
            st.success(f"✅ Berhasil menyimpan! Poin kamu: {points}")
        except Exception as e:
            st.error(f"Error: {e}")

# Tampilkan data
st.header("Statistik Komunitas")
df = get_waste_data()

if not df.empty:
    # Leaderboard
    st.subheader("Leaderboard")
    leaderboard = df.groupby("username")["poin"].sum().sort_values(ascending=False)
    st.bar_chart(leaderboard.head(10))
    
    # Total sampah
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Sampah Terkumpul", f"{df['berat'].sum():.1f} kg")
    with col2:
        st.metric("Total Poin Komunitas", f"{df['poin'].sum():,}")
        
    # Tabel data
    st.write("Data Transaksi Terakhir:")
    st.dataframe(df.sort_values("timestamp", ascending=False).head(10))
else:
    st.info("Belum ada data transaksi")
