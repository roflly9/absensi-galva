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
    
    .block-container {
        max-width: 500px !important;
        padding: 0px !important;
        margin: auto;
    }

    .stApp {
        background-color: #f8f9fa;
    }

    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        padding: 20px 10px;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        border-bottom: 4px solid #d32f2f;
    }
    
    .welcome-box {
        background-color: #0d47a1;
        color: white;
        padding: 8px;
        font-size: 11px;
        text-align: center;
        margin-bottom: 10px;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
    }

    /* FIX GRID: Memastikan kolom tidak turun ke bawah di HP */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
        padding: 0 15px !important;
    }

    div[data-testid="column"] {
        flex: 1 1 50% !important;
        min-width: 0px !important;
    }

    /* Tombol Menu Kotak */
    div.stButton > button {
        height: 120px !important; 
        width: 100% !important;
        border-radius: 15px !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 12px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        white-space: pre-wrap !important;
    }

    /* Warna Tombol */
    /* Tombol ke-1 (Mulai Absensi) - Biru */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { 
        background: linear-gradient(135deg, #1e88e5, #1565c0) !important; 
    }
    /* Tombol ke-2 (Tebus Denda) - Merah/Orange */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { 
        background: linear-gradient(135deg, #ff9800, #f57c00) !important; 
    }
    /* Tombol Admin Panel (Jika di baris baru) */
    .admin-btn div.stButton > button {
        background: linear-gradient(135deg, #455a64, #263238) !important;
    }

    .section-title {
        font-size: 15px;
        font-weight: 800;
        color: #0d47a1;
        margin: 20px 0px 10px 15px;
        border-left: 5px solid #d32f2f;
        padding-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- (Bagian Setup Data Tetap Sama) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for f in [folder_foto, folder_penebusan]:
        if not os.path.exists(f): os.makedirs(f)
inisialisasi_folder()

columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"]

if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">Sistem Absensi & Penebusan Denda</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)

    # BARIS 1: Mulai Absensi (Kiri) & Tebus Denda (Kanan)
    # Ini adalah kunci agar posisi tombol sesuai sketsa Anda
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        if st.button("📝\n\nMULAI\nABSENSI"): navigasi('Absensi')
    with row1_col2:
        if st.button("💰\n\nTEBUS\nDENDA"): navigasi('Tebus')

    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    
    # BARIS 2: Admin Panel
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
        if st.button("🔐\n\nADMIN\nPANEL"): navigasi('Admin')
        st.markdown('</div>', unsafe_allow_html=True)
    with row2_col2:
        st.empty() # Biarkan kosong agar Admin tetap di kiri

    # Statistik
    if not df_total.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        s1, s2 = st.columns(2)
        s1.metric("Terlambat", f"{total_terlambat}x")
        s2.metric("Tunggakan", f"Rp {hutang:,}")

# --- (Bagian Halaman Lainnya Tetap Sama) ---
elif st.session_state.page == 'Absensi':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.subheader("📝 Form Absensi")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Pilih Nama:", Karyawan_List)
    opsi = st.radio("Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Tugas Luar", "Cuti/Sakit"])
    waktu_skrg = datetime.now(timezone)
    if nama != "Pilih Nama":
        st.info(f"Jam: **{waktu_skrg.strftime('%H:%M:%S')} WITA**")
        img = st.camera_input("Ambil Selfie")
        if st.button("🚀 KIRIM DATA"):
            if img:
                is_late = (waktu_skrg.hour > 8 or (waktu_skrg.hour == 8 and waktu_skrg.minute > 5))
                denda = 10000 if (opsi == "Hadir di Kantor" and is_late) else 0
                data_baru = pd.DataFrame([[waktu_skrg.strftime("%Y-%m-%d"), waktu_skrg.strftime("%H:%M:%S"), nama, "TERLAMBAT" if denda > 0 else opsi.upper(), "", denda, "Belum Lunas" if denda > 0 else "Lunas", ""]], columns=columns)
                df_total = pd.concat([df_total, data_baru], ignore_index=True)
                df_total.to_excel(excel_file, index=False)
                st.success("Berhasil!"); time.sleep(1); navigasi('Dashboard')
            else: st.error("Foto Wajib!")

elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.subheader("💰 Tebus Denda")
    nama_tebus = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    if nama_tebus != "Pilih Nama":
        idx_h = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_h = df_total.loc[idx_h, 'Denda'].sum()
        if total_h > 0:
            st.error(f"Denda: Rp {total_h:,}")
            metode = st.radio("Metode:", ["Bayar Tunai", "Membersihkan Kantor"])
            bukti = st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])
            if st.button("🚀 AJUKAN"):
                if bukti:
                    df_total.loc[idx_h, 'Status Denda'] = "Menunggu Approval"
                    df_total.to_excel(excel_file, index=False)
                    st.success("Terkirim!"); time.sleep(1); navigasi('Dashboard')
        else: st.success("Bebas Denda.")

elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Sandi:", type="password")
    if pw == "galva123":
        t1, t2 = st.tabs(["📊 Data", "⚙️ Reset"])
        with t1: st.dataframe(df_total)
        with t2:
            if st.button("Hapus Semua"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()