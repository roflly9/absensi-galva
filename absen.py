import streamlit as st
from datetime import datetime
import os
import pandas as pd
import pytz 
import time

# --- 1. KONFIGURASI HALAMAN & UI ---
st.set_page_config(page_title="Absensi Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container Utama Mobile */
    .block-container {
        max-width: 450px !important;
        padding: 5px !important;
        margin: auto;
    }

    .stApp {
        background-color: #f4f7f9;
    }

    /* Banner Atas */
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 20px 10px;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 20px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .welcome-box {
        background-color: #d32f2f;
        color: white;
        padding: 4px 12px;
        font-size: 11px;
        text-align: center;
        width: fit-content;
        margin: -12px auto 8px auto;
        border-radius: 10px;
        border: 2px solid white;
        font-weight: bold;
    }

    /* GRID MENU - MEMAKSA 2 KOLOM SEJAJAR DI HP */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; 
        gap: 10px !important;
        padding: 0 15px !important;
        margin-bottom: -15px !important; /* Merapatkan jarak antar baris menu */
    }

    div[data-testid="column"] {
        flex: 1 1 50% !important;
        min-width: 0px !important;
    }

    /* Desain Tombol Menu Kotak */
    div.stButton > button {
        height: 120px !important; 
        width: 100% !important;
        border-radius: 20px !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1) !important;
        white-space: pre-wrap !important;
        transition: 0.3s ease;
    }

    div.stButton > button:active {
        transform: scale(0.95);
    }

    /* Warna Tombol Berdasarkan Posisi */
    /* Baris Aktivitas: Kolom 1 (Biru), Kolom 2 (Oranye) */
    div[data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(135deg, #1e88e5, #1565c0) !important;
    }
    div[data-testid="column"]:nth-of-type(2) button {
        background: linear-gradient(135deg, #ffa726, #f57c00) !important;
    }

    /* Menu Pengelola (Warna Gelap/Abu-abu) */
    .admin-btn button {
        background: linear-gradient(135deg, #607d8b, #455a64) !important;
    }

    /* Judul Seksi Rapat */
    .section-title {
        font-size: 14px;
        font-weight: 800;
        color: #333;
        margin: 20px 0 10px 15px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
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
        border: 1px solid #eee !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA & FILE ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

# Load data dari Excel jika ada
if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. LOGIKA HALAMAN ---

# --- DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)

    # BARIS 1: AKTIVITAS KARYAWAN (Grid 2 Kolom)
    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝\n\nMULAI\nABSENSI"): navigasi('Absensi')
    with col2:
        if st.button("💰\n\nTEBUS\nDENDA"): navigasi('Tebus')

    # BARIS 2: MENU PENGELOLA (Didekatkan ke atas)
    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
        if st.button("🔐\n\nADMIN\nPANEL"): navigasi('Admin')
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.empty() 

    # BARIS 3: STATUS HARI INI
    st.markdown('<p class="section-title">Status Hari Ini</p>', unsafe_allow_html=True)
    if not df_total.empty:
        total_telat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        total_denda = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        c_s1, c_s2 = st.columns(2)
        c_s1.metric("Terlambat", f"{total_telat}x")
        c_s2.metric("Tunggakan", f"Rp {total_denda:,}")
    else:
        st.info("Belum ada aktivitas hari ini.")

# --- HALAMAN ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Nama Karyawan:", karyawan)
    opsi = st.radio("Status Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tugas Luar", "Sakit/Cuti"])
    
    waktu_skrg = datetime.now(timezone)
    st.info(f"Waktu: **{waktu_skrg.strftime('%H:%M:%S')}** WITA")
    
    img = st.camera_input("Ambil Foto Selfie")
    
    if st.button("🚀 KIRIM ABSENSI"):
        if nama != "Pilih Nama" and img:
            # Aturan Denda: Lewat pukul 08:05 WITA
            is_telat = waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5)
            denda = 10000 if (opsi == "Hadir di Kantor" and is_telat) else 0
            status = "TERLAMBAT" if denda > 0 else opsi.upper()
            
            data_baru = pd.DataFrame([[
                waktu_skrg.strftime("%Y-%m-%d"), waktu_skrg.strftime("%H:%M:%S"),
                nama, status, "", denda, "Belum Lunas" if denda > 0 else "Lunas"
            ]], columns=columns)
            
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            
            st.success(f"Absensi Berhasil! {'(Terlambat)' if denda > 0 else ''}")
            time.sleep(1.5)
            navigasi('Dashboard')
        else:
            st.warning("Pilih Nama & Ambil Foto!")

# --- HALAMAN TEBUS DENDA ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    nama_tebus = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    if nama_tebus != "Pilih Nama":
        idx_h = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_h = df_total.loc[idx_h, 'Denda'].sum()
        
        if total_h > 0:
            st.error(f"Total Denda: Rp {total_h:,}")
            st.file_uploader("Upload Bukti Pembayaran", type=['jpg','png','jpeg'])
            if st.button("🚀 AJUKAN"):
                st.success("Terkirim! Menunggu konfirmasi admin.")
                time.sleep(1.5); navigasi('Dashboard')
        else:
            st.success("Anda tidak memiliki denda.")

# --- HALAMAN ADMIN ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    pw = st.text_input("Sandi Admin:", type="password")
    if pw == "galva123":
        st.write("### Rekap Data Absensi")
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Reset Data"):
            if os.path.exists(excel_file): os.remove(excel_file)
            st.rerun()