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
        # Pastikan kolom Tanggal bertipe datetime untuk grafik
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

if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)

    # SEKSI 1: MENU
    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)
    if st.button("📝 &nbsp; MULAI ABSENSI"): navigasi('Absensi')
    if st.button("💰 &nbsp; TEBUS DENDA"): navigasi('Tebus')

    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    if st.button("🔐 &nbsp; ADMIN PANEL"): navigasi('Admin')

    # SEKSI 2: STATUS & STATISTIK
    st.markdown('<p class="section-title">Status & Ringkasan</p>', unsafe_allow_html=True)
    
    if not df_total.empty:
        tgl_skrg = datetime.now(timezone).date()
        df_hari_ini = df_total[df_total['Tanggal'] == tgl_skrg]
        
        # Hitung Metrics
        total_telat_hari_ini = len(df_hari_ini[df_hari_ini['Status'] == 'TERLAMBAT'])
        tunggakan_total = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        setoran_lunas = df_total[df_total['Status Denda'] == 'Lunas']['Denda'].sum()
        
        # Baris 1: Metrics
        m1, m2 = st.columns(2)
        m1.metric("Telat Hari Ini", f"{total_telat_hari_ini}x")
        m2.metric("Total Setoran", f"Rp {setoran_lunas:,}")
        
        st.write("") # Spacer
        st.metric("Tunggakan Belum Bayar", f"Rp {tunggakan_total:,}", delta_color="inverse")

        # Grafik Terlambat 1 Minggu Terakhir
        st.write("")
        st.markdown("**Grafik Terlambat (7 Hari Terakhir)**")
        
        # Filter data 7 hari terakhir
        tgl_mulai = tgl_skrg - timedelta(days=6)
        df_7_hari = df_total[(df_total['Tanggal'] >= tgl_mulai) & (df_total['Status'] == 'TERLAMBAT')]
        
        if not df_7_hari.empty:
            # Grouping per tanggal
            grafik_data = df_7_hari.groupby('Tanggal').size().reset_index(name='Jumlah Karyawan')
            # Set index agar grafik terbaca dengan benar
            grafik_data = grafik_data.set_index('Tanggal')
            st.bar_chart(grafik_data, color="#d32f2f")
        else:
            st.caption("Belum ada data keterlambatan dalam 7 hari terakhir.")
            
    else:
        st.info("Belum ada data untuk ditampilkan.")

# --- HALAMAN FORM ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="app-header">📝 FORM ABSENSI</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu"): navigasi('Dashboard')
    
    karyawan = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama Anda:", karyawan)
    opsi = st.radio("Keterangan:", ["Hadir di Kantor", "Izin Terlambat", "Tugas Luar", "Sakit/Cuti"])
    
    waktu_skrg = datetime.now(timezone)
    st.info(f"🕒 Waktu Server: {waktu_skrg.strftime('%H:%M:%S')} WITA")
    img = st.camera_input("Ambil Foto Selfie")
    
    if st.button("🚀 KIRIM ABSENSI"):
        if nama != "Pilih Nama" and img:
            is_telat = waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5)
            denda = 10000 if (opsi == "Hadir di Kantor" and is_telat) else 0
            status = "TERLAMBAT" if denda > 0 else opsi.upper()
            
            data_baru = pd.DataFrame([[
                waktu_skrg.date(), waktu_skrg.strftime("%H:%M:%S"),
                nama, status, "", denda, "Belum Lunas" if denda > 0 else "Lunas"
            ]], columns=columns)
            
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            st.success("✅ Absensi Berhasil!")
            time.sleep(1.5)
            navigasi('Dashboard')
        else:
            st.error("Nama dan Foto wajib diisi!")

# --- HALAMAN TEBUS DENDA ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    st.markdown("### Daftar Tunggakan Anda")
    if not df_total.empty:
        df_tunggakan = df_total[df_total['Status Denda'] == 'Belum Lunas']
        if not df_tunggakan.empty:
            st.dataframe(df_tunggakan[['Tanggal', 'Nama', 'Denda']], use_container_width=True)
            st.warning("Silakan hubungi Admin untuk melakukan pembayaran.")
        else:
            st.success("Selamat! Tidak ada tunggakan denda.")
    else:
        st.info("Belum ada data.")

# --- HALAMAN ADMIN PANEL ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    pw = st.text_input("Password Admin:", type="password")
    if pw == "galva123":
        st.write("### Rekap Seluruh Data")
        # Fitur Update Status Denda
        if not df_total.empty:
            st.dataframe(df_total, use_container_width=True)
            
            st.divider()
            st.write("### Tandai Denda Lunas")
            idx_bayar = st.number_input("Masukkan No. Index dari tabel untuk konfirmasi bayar:", min_value=0, step=1)
            if st.button("Konfirmasi Pembayaran"):
                if idx_bayar in df_total.index:
                    df_total.at[idx_bayar, 'Status Denda'] = 'Lunas'
                    df_total.to_excel(excel_file, index=False)
                    st.success(f"Denda index {idx_bayar} berhasil dilunaskan!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Index tidak ditemukan.")
            
            st.download_button("📊 Download Excel", data=open(excel_file, "rb"), file_name="rekap_absensi.xlsx")