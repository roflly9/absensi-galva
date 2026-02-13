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
    
    /* Membatasi lebar kontainer agar pas dengan HP */
    .block-container {
        max-width: 480px !important;
        padding: 0px !important;
        margin: auto;
    }

    .stApp {
        background-color: #f0f2f6;
    }

    /* Styling Banner Atas */
    .app-header {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        padding: 18px 10px;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        border-bottom: 4px solid #d32f2f;
    }
    
    .welcome-box {
        background-color: #0d47a1;
        color: white;
        padding: 8px;
        font-size: 11px;
        text-align: center;
        margin-bottom: 15px;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
    }

    /* FLEXBOX UNTUK HP (360px-480px) */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        padding: 0 10px !important;
    }

    div[data-testid="column"] {
        flex: 1 !important;
        min-width: 0px !important;
    }

    /* Tombol Menu Kotak Lebih Rapat */
    div.stButton > button {
        height: 110px !important; /* Ukuran disesuaikan agar tidak terlalu tinggi di HP */
        width: 100% !important;
        border-radius: 12px !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 12px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
        margin: 0px !important;
        padding: 5px !important;
    }

    /* WARNA TOMBOL */
    div.stButton:nth-of-type(1) > button { background: linear-gradient(135deg, #1e88e5, #1565c0) !important; } 
    div.stButton:nth-of-type(2) > button { background: linear-gradient(135deg, #e53935, #c62828) !important; }
    div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #455a64, #263238) !important; }

    .section-title {
        font-size: 14px;
        font-weight: 800;
        color: #0d47a1;
        margin: 10px 0px 5px 15px;
        border-left: 3px solid #d32f2f;
        padding-left: 8px;
    }

    /* Penyesuaian Metric untuk layar kecil */
    [data-testid="stMetric"] {
        padding: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA ---
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

# --- 3. DASHBOARD UTAMA (MOBILE PORTRAIT OPTIMIZED) ---
if st.session_state.page == 'Dashboard':
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">Sistem Absensi & Penebusan Denda</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Aktivitas Karyawan</p>', unsafe_allow_html=True)

    # Baris 1: Tombol Berjajar Rapat
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝\n\nMULAI\nABSENSI"): navigasi('Absensi')
    with c2:
        if st.button("💰\n\nTEBUS\nDENDA"): navigasi('Tebus')

    st.markdown('<p class="section-title">Menu Pengelola</p>', unsafe_allow_html=True)
    
    # Baris 2: Admin Panel
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🔐\n\nADMIN\nPANEL"): navigasi('Admin')
    with c4:
        st.write("") # Penyeimbang agar grid tetap 50/50

    # Statistik
    if not df_total.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        # Metric dalam satu baris
        s1, s2 = st.columns(2)
        s1.metric("Terlambat", f"{total_terlambat}x")
        s2.metric("Denda", f"Rp {hutang:,}")

# --- HALAMAN LAINNYA (ABSENSI, TEBUS, ADMIN) TETAP SAMA ---
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
                st.success("Terkirim!"); time.sleep(1); navigasi('Dashboard')
            else: st.error("Ambil Foto!")

elif st.session_state.page == 'Tebus':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.subheader("💰 Tebus Denda")
    nama_tebus = st.selectbox("Pilih Nama:", ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"])
    if nama_tebus != "Pilih Nama":
        idx_h = df_total[(df_total['Nama'] == nama_tebus) & (df_total['Status Denda'] == 'Belum Lunas')].index
        total_h = df_total.loc[idx_h, 'Denda'].sum()
        if total_h > 0:
            st.error(f"Tunggakan: Rp {total_h:,}")
            metode = st.radio("Metode:", ["Bayar Tunai", "Membersihkan Kantor"])
            bukti = st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])
            if st.button("🚀 AJUKAN"):
                if bukti:
                    df_total.loc[idx_h, 'Status Denda'] = "Menunggu Approval"
                    df_total.to_excel(excel_file, index=False)
                    st.success("Diproses!"); time.sleep(1); navigasi('Dashboard')
        else: st.success("Bebas Denda.")

elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Sandi:", type="password")
    if pw == "galva123":
        t1, t2 = st.tabs(["📊 Laporan", "⚙️ Reset"])
        with t1: st.dataframe(df_total)
        with t2:
            if st.button("Hapus Data"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()