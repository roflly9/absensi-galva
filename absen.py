import streamlit as st
from datetime import datetime, timedelta
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
    
    .block-container {
        max-width: 100% !important;
        padding: 0.5rem !important;
        margin: auto;
        overflow-x: hidden;
    }

    .stApp {
        background-color: #f8f9fa;
    }

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
        z-index: 10;
    }

    div.stButton > button {
        height: 65px !important; 
        width: 100% !important;
        border-radius: 15px !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease;
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%) !important;
    }

    div.stButton > button:active {
        transform: scale(0.98);
        background: #0d47a1 !important;
    }

    .section-title {
        font-size: 14px;
        font-weight: 800;
        color: #0d47a1;
        margin: 25px 0 10px 10px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
    }
    .section-title::before {
        content: "";
        width: 5px;
        height: 18px;
        background: #d32f2f;
        margin-right: 10px;
        border-radius: 3px;
    }

    div[data-testid="stMetric"] {
        background: white !important;
        padding: 10px !important;
        border-radius: 15px !important;
        border: 1px solid #e3f2fd !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA & FILE ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.date
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. LOGIKA HALAMAN ---

# --- DASHBOARD ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    if st.button("📝 &nbsp; MULAI ABSENSI"): navigasi('Absensi')
    if st.button("💰 &nbsp; TEBUS DENDA"): navigasi('Tebus')

    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    if st.button("🔐 &nbsp; ADMIN PANEL"): navigasi('Admin')

    st.markdown('<p class="section-title">Status & Ringkasan</p>', unsafe_allow_html=True)
    if not df_total.empty:
        tgl_skrg = datetime.now(timezone).date()
        df_hari_ini = df_total[df_total['Tanggal'] == tgl_skrg]
        total_telat_hari_ini = len(df_hari_ini[df_hari_ini['Status'] == 'TERLAMBAT'])
        tunggakan_total = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        setoran_lunas = df_total[df_total['Status Denda'] == 'Lunas']['Denda'].sum()
        
        m1, m2 = st.columns(2)
        m1.metric("Telat Hari Ini", f"{total_telat_hari_ini}x")
        m2.metric("Total Setoran", f"Rp {setoran_lunas:,}")
        st.metric("Tunggakan Belum Bayar", f"Rp {tunggakan_total:,}", delta_color="inverse")
    else:
        st.info("Belum ada data untuk ditampilkan.")

# --- HALAMAN FORM ABSENSI (UPDATE) ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    st.markdown("### Isi Data Kehadiran")
    
    karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Nama Karyawan:", karyawan)
    
    opsi = st.radio("Opsi Kehadiran:", [
        "Hadir di kantor",
        "Izin terlambat",
        "Tidak masuk kantor Cuti/Sakit",
        "Tugas Luar kota",
        "Langsung ke customer"
    ])
    
    # --- LOGIKA WAKTU & DENDA ---
    waktu_skrg = datetime.now(timezone)
    jam_skrg = waktu_skrg.time()
    batas_absen = datetime.strptime("08:05:00", "%H:%M:%S").time()
    
    # Cek apakah terlambat (hanya berlaku untuk 'Hadir di kantor')
    is_telat = False
    if opsi == "Hadir di kantor" and jam_skrg > batas_absen:
        is_telat = True
    
    # Tampilkan Status Real-time
    st.divider()
    c1, c2 = st.columns(2)
    c1.info(f"🕒 **Waktu:** {waktu_skrg.strftime('%H:%M:%S')} WITA")
    
    if is_telat:
        c2.error("⚠️ **Status:** TERLAMBAT")
        st.warning("Anda terlambat (lewat jam 08:05). Denda **Rp 10.000** akan dicatat.")
    else:
        c2.success("✅ **Status:** TEPAT WAKTU")

    # Input Foto
    img = st.camera_input("Ambil Foto Selfie")
    
    if st.button("🚀 KIRIM ABSENSI"):
        if nama != "Pilih Nama" and img:
            # Hitung denda
            denda = 10000 if is_telat else 0
            status_final = "TERLAMBAT" if is_telat else opsi.upper()
            
            # Simpan Data
            data_baru = pd.DataFrame([[
                waktu_skrg.date(), 
                waktu_skrg.strftime("%H:%M:%S"),
                nama, 
                status_final, 
                opsi, 
                denda, 
                "Belum Lunas" if denda > 0 else "Lunas"
            ]], columns=columns)
            
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            
            # Notifikasi Berhasil
            st.balloons()
            st.success(f"✅ Berhasil! Absensi {nama} telah tercatat.")
            time.sleep(2)
            navigasi('Dashboard')
        else:
            st.error("Gagal! Pastikan Nama sudah dipilih dan Foto sudah diambil.")

# --- HALAMAN LAINNYA (Tebus & Admin) ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.dataframe(df_total[df_total['Status Denda'] == 'Belum Lunas'][['Tanggal', 'Nama', 'Denda']], use_container_width=True)

elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        st.dataframe(df_total, use_container_width=True)