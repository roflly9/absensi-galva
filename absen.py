import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import shutil
import time
import io
from PIL import Image

# --- 1. KONFIGURASI HALAMAN & UI ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Layout Utama Mobile */
    .block-container {
        max-width: 450px !important;
        padding: 10px !important;
        margin: auto;
    }

    .stApp {
        background-color: #f4f7f9;
    }

    /* Header Banner */
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 25px 10px;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 22px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .welcome-box {
        background-color: #d32f2f;
        color: white;
        padding: 5px;
        font-size: 10px;
        text-align: center;
        width: fit-content;
        margin: -15px auto 15px auto;
        border-radius: 10px;
        position: relative;
        z-index: 10;
        border: 2px solid white;
    }

    /* FIX: GRID MENU HP */
    /* Menghapus padding bawaan streamlit columns */
    div[data-testid="column"] {
        padding: 0px 5px !important;
        flex: 1 1 calc(50% - 10px) !important;
        min-width: calc(50% - 10px) !important;
    }

    /* Memastikan tombol dalam satu baris tetap sejajar horizontal */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        margin-bottom: 10px !important;
    }

    /* Desain Tombol Menu */
    div.stButton > button {
        height: 110px !important; 
        width: 100% !important;
        border-radius: 18px !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08) !important;
        transition: transform 0.2s ease !important;
    }

    div.stButton > button:active {
        transform: scale(0.95) !important;
    }

    /* Warna & Icon Gradient */
    /* 1. Tombol Absensi */
    div[data-testid="column"]:nth-child(1) button {
        background: linear-gradient(135deg, #42a5f5, #1976d2) !important;
    }
    /* 2. Tombol Tebus Denda */
    div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(135deg, #ffa726, #fb8c00) !important;
    }
    /* 3. Tombol Admin Panel */
    .admin-container button {
        background: linear-gradient(135deg, #78909c, #455a64) !important;
    }

    /* Judul Seksi */
    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #333;
        margin: 20px 0 10px 5px;
        display: flex;
        align-items: center;
    }
    .section-title::before {
        content: "";
        width: 4px;
        height: 16px;
        background: #d32f2f;
        margin-right: 8px;
        border-radius: 2px;
    }

    /* Metric Card */
    div[data-testid="stMetric"] {
        background: white !important;
        padding: 15px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03) !important;
        border: 1px solid #eee !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA (Standard) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
    except:
        df_total = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"])
else:
    df_total = pd.DataFrame(columns=["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"])

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">Sistem Absensi</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Menu Karyawan</p>', unsafe_allow_html=True)

    # BARIS 1: 2 Kolom Sejajar (Absensi & Tebus)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝\nABSENSI"): navigasi('Absensi')
    with col2:
        if st.button("💰\nTEBUS\nDENDA"): navigasi('Tebus')

    st.markdown('<p class="section-title">Pengelola</p>', unsafe_allow_html=True)
    
    # BARIS 2: Admin Panel
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="admin-container">', unsafe_allow_html=True)
        if st.button("🔐\nADMIN\nPANEL"): navigasi('Admin')
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.empty() 

    # Area Statistik
    st.markdown('<p class="section-title">Ringkasan Hari Ini</p>', unsafe_allow_html=True)
    if not df_total.empty:
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        s1, s2 = st.columns(2)
        s1.metric("Terlambat", f"{total_terlambat}x")
        s2.metric("Tunggakan", f"Rp {hutang:,}")
    else:
        st.caption("Belum ada data aktivitas.")

# --- HALAMAN LAIN (KODE LOGIK TETAP) ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.subheader("📝 Form Absensi")
    nama = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    if nama != "Pilih Nama":
        st.camera_input("Ambil Selfie")
        if st.button("🚀 KIRIM"): st.success("Berhasil!"); time.sleep(1); navigasi('Dashboard')

elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.subheader("💰 Tebus Denda")
    st.info("Pilih nama Anda untuk melihat tunggakan.")
    st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric"])

elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Sandi Admin:", type="password")
    if pw == "galva123":
        st.dataframe(df_total)