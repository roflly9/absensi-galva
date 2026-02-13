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
    
    .stApp {
        background-color: #f4f7f6;
    }

    /* Styling Banner Atas (Sesuai Gambar) */
    .app-header {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        padding: 20px;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 22px;
        margin-bottom: 0px;
        border-bottom: 4px solid #ffd600;
    }
    
    .welcome-box {
        background-color: #2e7d32;
        color: white;
        padding: 10px;
        font-size: 14px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* GRID MENU (Sesuai Gambar) */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 calc(50% - 10px) !important;
        min-width: 45% !important;
        padding: 5px !important;
    }

    /* Tombol Menu Kotak Berwarna */
    div.stButton > button {
        height: 160px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 15px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }

    /* Warna Tombol Spesifik */
    /* Tombol Absensi - Orange */
    div.stButton:nth-of-type(1) > button { background-color: #ffa726 !important; } 
    /* Tombol Tebus - Biru Ungu */
    div.stButton:nth-of-type(2) > button { background-color: #5c6bc0 !important; }
    /* Tombol Admin - Teal */
    div.stButton:nth-of-type(3) > button { background-color: #26a69a !important; }

    /* Judul Seksi */
    .section-title {
        font-size: 16px;
        font-weight: bold;
        color: #333;
        margin: 10px 0px 10px 10px;
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

# --- 3. DASHBOARD UTAMA (SESUAI GAMBAR REFERENSI) ---
if st.session_state.page == 'Dashboard':
    # Header Biru/Hijau sesuai Gambar
    st.markdown('<div class="app-header">🏢 GALVA MANADO</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-box">Welcome to Galva Manado Family<br>Absensi & Penebusan Denda</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Menu Utama</p>', unsafe_allow_html=True)

    # Baris 1: Absensi & Tebus
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝\n\nMULAI\nABSENSI"): navigasi('Absensi')
    with col2:
        if st.button("💰\n\nTEBUS\nDENDA"): navigasi('Tebus')

    # Baris 2: Admin Panel
    st.markdown('<p class="section-title">Akses Admin</p>', unsafe_allow_html=True)
    col3, col4 = st.columns(2) # Tetap pakai 2 kolom agar ukuran box sama dengan atas
    with col3:
        if st.button("🔐\n\nADMIN\nPANEL"): navigasi('Admin')

    # Statistik Singkat di bawah
    if not df_total.empty:
        st.write("---")
        total_terlambat = len(df_total[df_total['Status'] == 'TERLAMBAT'])
        hutang = df_total[df_total['Status Denda'] == 'Belum Lunas']['Denda'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Terlambat", f"{total_terlambat}x")
        c2.metric("Tunggakan", f"Rp {hutang:,}")

# --- 4. HALAMAN ABSENSI (ISI TETAP) ---
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
            else:
                st.error("Foto Wajib!")

# --- 5. HALAMAN TEBUS (ISI TETAP) ---
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
                    st.success("Terkirim!"); time.sleep(1); navigasi('Dashboard')
        else: st.success("Bebas Denda.")

# --- 6. HALAMAN ADMIN (ISI TETAP) ---
elif st.session_state.page == 'Admin':
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    pw = st.text_input("Sandi Admin:", type="password")
    if pw == "galva123":
        t1, t2 = st.tabs(["📊 Laporan", "⚙️ Reset"])
        with t1: st.dataframe(df_total)
        with t2:
            if st.button("Hapus Semua Data"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()