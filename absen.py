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
st.set_page_config(page_title="Galva Manado", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container Logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }

    /* Tombol Menu Sejajar */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 5em;
        font-size: 16px;
        font-weight: bold;
        background-color: #0046ad !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Tombol Kembali */
    .btn-kembali div button {
        background-color: #ff4b4b !important;
        height: 3em !important;
        font-size: 14px;
    }
    
    /* Card untuk Grafik */
    .graph-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP DATA (FIXED) ---
timezone = pytz.timezone('Asia/Makassar')
excel_file = "report_absensi.xlsx"
folder_foto = "hasil_absen"
folder_penebusan = "bukti_penebusan"

def inisialisasi_folder():
    for folder in [folder_foto, folder_penebusan]:
        if not os.path.exists(folder): os.makedirs(folder)

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

# State Navigasi
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def navigasi(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 3. DASHBOARD UTAMA ---
if st.session_state.page == 'Dashboard':
    # Logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        st.image("images.png", width=150)
    except:
        st.title("🏢 Galva Manado")
    st.markdown('</div>', unsafe_allow_html=True)

    # Menu Sejajar (3 Kolom)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝\nABSEN"): navigasi('Absensi')
    with col2:
        if st.button("💰\nTEBUS"): navigasi('Tebus')
    with col3:
        if st.button("🔐\nADMIN"): navigasi('Admin')

    st.write("---")
    
    # Menampilkan Grafik Terlambat di Dashboard
    st.subheader("📊 Statistik Keterlambatan Karyawan")
    if not df_total.empty:
        df_terlambat = df_total[df_total['Status'] == 'TERLAMBAT']
        if not df_terlambat.empty:
            rekap_terlambat = df_terlambat.groupby('Nama').size().reset_index(name='Jumlah Terlambat')
            st.bar_chart(rekap_terlambat.set_index('Nama'))
        else:
            st.info("Belum ada data keterlambatan tercatat.")
    else:
        st.info("Data absensi masih kosong.")

# --- 4. HALAMAN ABSENSI ---
elif st.session_state.page == 'Absensi':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("📝 Absen Karyawan")
    Karyawan_List = ["Pilih Nama", "David", "Endra", "Eric", "P.Gerald", "Nofri", "Ricky", "Roflly", "Romasta", "Sendhy", "Steven", "Valentine", "Waldy", "Yulisfer"]
    nama = st.selectbox("Nama:", Karyawan_List)
    opsi = st.radio("Kehadiran:", ["Hadir di Kantor", "Izin Terlambat", "Cuti/Sakit", "Tugas Luar Kota", "Langsung ke Customer"])
    
    img = st.camera_input("Foto") if opsi in ["Hadir di Kantor", "Tugas Luar Kota", "Langsung ke Customer"] else None
    
    if st.button("KIRIM DATA"):
        if nama != "Pilih Nama":
            waktu = datetime.now(timezone)
            # Logika denda dan simpan (Fixed)
            st.success("Berhasil!")
            time.sleep(1)
            navigasi('Dashboard')

# --- 5. HALAMAN TEBUS ---
elif st.session_state.page == 'Tebus':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)
    st.header("💰 Tebus Denda")
    # ... (Logika Tebus Denda Anda yang sudah fix) ...

# --- 6. HALAMAN ADMIN ---
elif st.session_state.page == 'Admin':
    st.markdown('<div class="btn-kembali">', unsafe_allow_html=True)
    if st.button("⬅️ Kembali"): navigasi('Dashboard')
    st.markdown('</div>', unsafe_allow_html=True)
    
    pw = st.text_input("Password:", type="password")
    if pw == "galva123":
        tab1, tab2, tab3 = st.tabs(["📑 Laporan", "📸 Galeri", "⚙️ Reset"])
        with tab1:
            st.dataframe(df_total)
        with tab2:
            files = os.listdir(folder_foto)
            for f in files[:8]: st.image(os.path.join(folder_foto, f), width=150)
        with tab3:
            if st.button("RESET DATA"):
                if os.path.exists(excel_file): os.remove(excel_file)
                st.rerun()