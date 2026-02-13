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

    /* GRID MENU - SANGAT RAPAT */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        padding: 0 10px !important;
        margin-bottom: -15px !important; /* Menghilangkan jarak antar baris */
    }

    div[data-testid="column"] {
        flex: 1 1 50% !important;
        min-width: 0px !important;
    }

    /* Tombol Menu */
    div.stButton > button {
        height: 100px !important; 
        width: 100% !important;
        border-radius: 15px !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.06) !important;
        white-space: pre-wrap !important;
    }

    /* Warna Tombol */
    div[data-testid="column"]:nth-child(1) button { background: linear-gradient(135deg, #42a5f5, #1976d2) !important; }
    div[data-testid="column"]:nth-child(2) button { background: linear-gradient(135deg, #ffa726, #fb8c00) !important; }
    .admin-container button { background: linear-gradient(135deg, #78909c, #455a64) !important; }

    /* Judul Seksi Rapat */
    .section-title {
        font-size: 13px;
        font-weight: 800;
        color: #0d47a1;
        margin: 12px 0 5px 12px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .section-title::before {
        content: "";
        width: 4px;
        height: 14px;
        background: #d32f2f;
        margin-right: 8px;
        border-radius: 2px;
    }

    /* Metric Card */
    div[data-testid="stMetric"] {
        background: white !important;
        padding: 10px !important;
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA & FOLDER ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda"]

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

# --- DASHBOARD ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">PRESENSI & DENDA</div>', unsafe_allow_html=True)

    # BARIS 1: MENU UTAMA
    st.markdown('<p class="section-title">Aktivitas</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝\nABSENSI"): navigasi('Absensi')
    with c2:
        if st.button("💰\nTEBUS\nDENDA"): navigasi('Tebus')

    # BARIS 2: ADMIN (RAPAT)
    st.markdown('<p class="section-title">Pengelola</p>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="admin-container">', unsafe_allow_html=True)
        if st.button("🔐\nADMIN\nPANEL"): navigasi('Admin')
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.empty() 

    # STATISTIK (DAPAT DILIHAT LANGSUNG)
    st.markdown('<p class="section-title">Status Hari Ini</p>', unsafe_allow_html=True)
    if not df_total.empty:
        total_telat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        total_denda = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        s1, s2 = st.columns(2)
        s1.metric("Terlambat", f"{total_telat}x")
        s2.metric("Total Denda", f"Rp {total_denda:,}")
    else:
        st.info("Belum ada data hari ini.")

# --- FORM ABSENSI ---
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
            # Hitung Denda (Batas 08:05)
            jam_telat = waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5)
            denda = 10000 if (opsi == "Hadir di Kantor" and jam_telat) else 0
            status = "TERLAMBAT" if denda > 0 else opsi.upper()
            
            # Simpan Data
            data_baru = pd.DataFrame([[
                waktu_skrg.strftime("%Y-%m-%d"),
                waktu_skrg.strftime("%H:%M:%S"),
                nama, status, "", denda, 
                "Belum Lunas" if denda > 0 else "Lunas"
            ]], columns=columns)
            
            df_total = pd.concat([df_total, data_baru], ignore_index=True)
            df_total.to_excel(excel_file, index=False)
            
            st.success(f"Absensi Berhasil! {'(Terlambat)' if denda > 0 else ''}")
            time.sleep(1.5)
            navigasi('Dashboard')
        else:
            st.warning("Pilih Nama & Ambil Foto!")

# --- TEBUS DENDA ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="app-header">💰 TEBUS DENDA</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    nama_tebus = st.selectbox("Nama Anda:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    
    if nama_tebus != "Pilih Nama":
        hutang_idx = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_hutang = df_total.loc[hutang_idx, 'Denda'].sum()
        
        if total_hutang > 0:
            st.error(f"Total Tunggakan: Rp {total_hutang:,}")
            metode = st.radio("Metode Penebusan:", ["Bayar Tunai", "Membersihkan Kantor"])
            bukti = st.file_uploader("Upload Bukti Transfer/Foto", type=['jpg','png','jpeg'])
            
            if st.button("🚀 AJUKAN PENEBUSAN"):
                if bukti:
                    df_total.loc[hutang_idx, 'Status Denda'] = "Menunggu Approval"
                    df_total.to_excel(excel_file, index=False)
                    st.success("Permintaan diproses! Menunggu Admin.")
                    time.sleep(1.5)
                    navigasi('Dashboard')
                else:
                    st.warning("Upload bukti terlebih dahulu!")
        else:
            st.success("Selamat! Anda tidak memiliki tunggakan denda.")

# --- ADMIN PANEL ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="app-header">🔐 ADMIN PANEL</div>', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    
    pw = st.text_input("Sandi Keamanan:", type="password")
    if pw == "galva123":
        st.write("### Data Seluruh Karyawan")
        st.dataframe(df_total, use_container_width=True)
        
        if st.button("🗑️ Reset Data"):
            if os.path.exists(excel_file): os.remove(excel_file)
            st.rerun()