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
    /* Menghilangkan elemen default Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* FIX MOBILE: Memaksa konten pas di layar (No Horizontal Scroll) */
    .block-container {
        max-width: 100% !important;
        padding: 0.5rem !important;
        margin: auto;
        overflow-x: hidden;
    }

    /* FIX GRID: Memaksa kolom tetap 50:50 di HP */
    [data-testid="column"] {
        width: 48% !important;
        flex: 1 1 48% !important;
        min-width: 48% !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        gap: 0.4rem !important;
        margin-bottom: -10px !important;
    }

    .stApp {
        background-color: #f8f9fa;
    }

    /* Banner Header Blue (Sesuai Gambar) */
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 25px 10px;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 18px;
        border-radius: 0 0 25px 25px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .welcome-box {
        background-color: #d32f2f;
        color: white;
        padding: 5px 15px;
        font-size: 10px;
        text-align: center;
        width: fit-content;
        margin: -30px auto 15px auto;
        border-radius: 10px;
        border: 2px solid white;
        font-weight: bold;
        position: relative;
    }

    /* Tombol Menu Kotak (Sesuai Referensi Gambar) */
    div.stButton > button {
        height: 125px !important; 
        width: 100% !important;
        border-radius: 20px !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1) !important;
        white-space: normal !important;
        line-height: 1.4 !important;
        transition: transform 0.2s ease;
    }

    div.stButton > button:active {
        transform: scale(0.92);
    }

    /* Ikon di dalam tombol */
    .btn-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }

    /* Pengaturan Warna Tombol */
    /* Baris 1 Kolom 1: Biru */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-child(1) button {
        background: linear-gradient(135deg, #42a5f5, #1976d2) !important;
    }
    /* Baris 1 Kolom 2: Biru Tua / Oranye (Bisa disesuaikan) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(135deg, #2196f3, #0d47a1) !important;
    }
    /* Baris 2 (Admin): Biru Gelap */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-child(1) button {
        background: linear-gradient(135deg, #64b5f6, #1565c0) !important;
    }

    /* Judul Seksi (Aktivitas Karyawan & Menu Pengelola) */
    .section-title {
        font-size: 14px;
        font-weight: 800;
        color: #0d47a1;
        margin: 20px 0 10px 10px;
        display: flex;
        align-items: center;
    }
    .section-title::before {
        content: "";
        width: 5px;
        height: 18px;
        background: #d32f2f;
        margin-right: 10px;
        border-radius: 3px;
    }

    /* Metric Statistik */
    div[data-testid="stMetric"] {
        background: white !important;
        padding: 15px !important;
        border-radius: 18px !important;
        border: 1px solid #e3f2fd !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

if os.path.exists(excel_file):
    try: df_total = pd.read_excel(excel_file)
    except: df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)

    # SEKSI 1: AKTIVITAS KARYAWAN (2 Kolom Berdampingan)
    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝\n\nMULAI\nABSENSI"): navigasi('Absensi')
    with col2:
        if st.button("💰\n\nTEBUS\nDENDA"): navigasi('Tebus')

    # SEKSI 2: MENU PENGELOLA (Dibawahnya)
    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        if st.button("🔐\n\nADMIN\nPANEL"): navigasi('Admin')
    with col4:
        st.empty() # Membiarkan sebelah kanan admin panel kosong agar rapi

    # SEKSI 3: STATUS HARI INI
    st.markdown('<p class="section-title">Status Hari Ini</p>', unsafe_allow_html=True)
    if not df_total.empty:
        tgl_skrg = datetime.now(timezone).strftime("%Y-%m-%d")
        df_hari_ini = df_total[df_total['Tanggal'] == tgl_skrg]
        
        total_telat = len(df_hari_ini[df_hari_ini['Status'] == 'TERLAMBAT'])
        total_denda = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Terlambat", f"{total_telat}x")
        c2.metric("Tunggakan", f"Rp {total_denda:,}")
    else:
        st.info("Belum ada data hari ini.")

# --- HALAMAN FORM ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    with st.container():
        karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
        nama = st.selectbox("Pilih Nama Anda:", karyawan)
        opsi = st.radio("Keterangan:", ["Hadir di Kantor", "Izin Terlambat", "Tugas Luar", "Sakit/Cuti"])
        
        waktu_skrg = datetime.now(timezone)
        st.warning(f"🕒 Jam Sekarang: {waktu_skrg.strftime('%H:%M:%S')} WITA")
        
        img = st.camera_input("Ambil Foto Selfie")
        
        if st.button("🚀 KIRIM ABSENSI"):
            if nama != "Pilih Nama" and img:
                # Cek keterlambatan > 08:05
                is_telat = waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5)
                denda = 10000 if (opsi == "Hadir di Kantor" and is_telat) else 0
                status = "TERLAMBAT" if denda > 0 else opsi.upper()
                
                data_baru = pd.DataFrame([[
                    waktu_skrg.strftime("%Y-%m-%d"), waktu_skrg.strftime("%H:%M:%S"),
                    nama, status, "", denda, "Belum Lunas" if denda > 0 else "Lunas"
                ]], columns=columns)
                
                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                df_total.to_excel(excel_file, index=False)
                
                st.success("✅ Absensi Berhasil!")
                time.sleep(1.5)
                navigasi('Dashboard')
            else:
                st.error("Silakan pilih nama dan ambil foto!")

# --- HALAMAN ADMIN PANEL ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    pw = st.text_input("Masukkan Password Admin:", type="password")
    if pw == "galva123":
        st.write("### Rekap Data Absensi")
        st.dataframe(df_total, use_container_width=True)
        
        st.download_button(
            label="📊 Download Excel",
            data=open(excel_file, "rb"),
            file_name="rekap_absensi_galva.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )