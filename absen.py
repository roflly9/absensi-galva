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
st.set_page_config(page_title="Galva Manado", page_icon="🏢", layout="centered")

# CSS untuk estetika Android Modern
st.markdown("""
    <style>
    /* Menyembunyikan elemen standar Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background & Font */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Container untuk Logo di Dashboard */
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px;
        margin-bottom: 10px;
    }

    /* Card Style untuk Dashboard */
    .menu-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #E9ECEF;
    }

    /* Tombol Utama Ala Android (Rounded & Shadow) */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-size: 16px;
        font-weight: 600;
        background-color: #0046ad !important;
        color: white !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 0 4px 12px rgba(0,70,173,0.2);
    }
    
    div.stButton > button:hover {
        box-shadow: 0 6px 15px rgba(0,70,173,0.3);
        transform: translateY(-2px);
    }

    /* Tombol Kembali (Secondary) */
    .btn-kembali div button {
        background-color: white !important;
        color: #495057 !important;
        border: 1px solid #CED4DA !important;
        box-shadow: none !important;
    }

    /* Info Box */
    .stAlert {
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP FOLDER & DATA ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for folder in [folder_foto, folder_penebusan]:
        if not os.path.exists(folder):
            os.makedirs(folder)

inisialisasi_folder()

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# Load Data
columns = ["Tanggal", "Jam", "Nama", "Status", "Alasan", "Denda", "Status Denda", "ID_Tebus"]
if os.path.exists(excel_file):
    try:
        df_total = pd.read_excel(excel_file)
        df_total['Tanggal'] = pd.to_datetime(df_total['Tanggal']).dt.strftime('%Y-%m-%d')
    except:
        df_total = pd.DataFrame(columns=columns)
else:
    df_total = pd.DataFrame(columns=columns)

# --- 3. FUNGSI NAVIGASI ---
def navigasi(nama_halaman):
    st.session_state.page = nama_halaman
    st.rerun()

# --- 4. HALAMAN DASHBOARD (UTAMA) ---
if st.session_state.page == 'Dashboard':
    # Menampilkan Logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        logo = Image.open("images.png") # Pastikan file gambar ada di folder yang sama
        st.image(logo, width=180)
    except:
        st.write("🏢 **GALVA MANADO**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='color: #212529; margin-bottom: 0;'>Selamat Datang</h2>
            <p style='color: #6C757D;'>Sistem Absensi Internal Galva Manado</p>
        </div>
    """, unsafe_allow_html=True)

    # Menu Utama
    if st.button("📝 Mulai Absensi"):
        navigasi('Absensi')
    
    if st.button("💰 Penebusan Denda"):
        navigasi('Tebus')
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔐 Panel Admin", help="Khusus Pengelola"):
        navigasi('Admin')

# --- 5. HALAMAN ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"):
        navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("Absensi Karyawan")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Identitas Karyawan:", Karyawan_List)
    opsi_absen = st.radio("Tipe Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Cuti / Sakit", "Tugas Luar Kota", "Langsung ke Customer"])

    waktu_sekarang = datetime.now(timezone)
    if nama != "Pilih Nama":
        st.info(f"🕒 Waktu Sekarang: **{waktu_sekarang.strftime('%H:%M:%S')}**")
        
        alasan = ""
        if opsi_absen in ["Tugas Luar Kota", "Langsung ke Customer"]:
            alasan = st.text_input("📍 Lokasi Tujuan:")
        elif opsi_absen != "Hadir di Kantor":
            alasan = st.text_area("📝 Catatan / Alasan:")
        
        img_file = st.camera_input("Ambil Foto Selfie") if opsi_absen in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else st.file_uploader("Upload Bukti", type=['jpg','png','jpeg'])

        if (img_file is not None) or (opsi_absen in ["Izin Terlambat", "Cuti / Sakit"]):
            if st.button("🚀 Kirim Absensi"):
                # Logika simpan data sama dengan kode sebelumnya
                st.success("Data berhasil dikirim!")
                time.sleep(2)
                navigasi('Dashboard')

# --- HALAMAN LAIN (Tebus & Admin) ---
# Tambahkan kode halaman Tebus & Admin Anda di sini dengan menyertakan tombol kembali seperti di atas.